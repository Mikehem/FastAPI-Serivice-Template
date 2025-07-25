#####################################################################
# Copyright(C), 2023 xxx Private Limited. All Rights Reserved
# Unauthorized copying of this file, via any medium is
# strictly prohibited
#
# Proprietary and confidential
# email: care@xxx.in
#####################################################################
import asyncio
import inspect
import types
from functools import wraps
from typing import Callable, Dict, Tuple

from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Tracer
from opentelemetry import trace

# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from app.core.config import cfg

# Resource can be required for some backends, e.g. Jaeger
# If resource wouldn't be set - traces wouldn't appears in Jaeger
class xxxLTM:
    class dummy_counter:
        def __init__(self, name, description) -> None:
            self.value = 0
            self.name = name
            self.description = description
            
        def add(self, count:int) -> None:
            self.value += count
            
        def reset(self):
            self.value = 0
            
        def __str__(self) -> str:
            return self.value
            
    def __init__(self) -> None:
        self.COUNTERS = {}
        self.TRACER = None
        self.METER = None
        self._configure()
        
    def _configure(self) -> None:
        if "OLTP" in cfg.processing and "Type" in cfg.processing.OLTP and cfg.processing.OLTP.Type.upper() == "OTEL":
            self._configure_otel()
        else:
            self._configure_simple_trace()
        
    def set_std_counters(self) -> None:
        """Set xxx level standard counters."""
        self.set_counter(name="Page Counter", description="Counter to track count of pages.")
        self.set_counter(name="Document Counter", description="Counter to track count of documents.")
        self.set_counter(name="KYC Counter", description="Counter to track count of kyc pages.")
        
        
    def set_counter(self, name=str, description=str) -> None:
        """Sets a custom counter."""
        cap_name = name.upper().replace(" ", "_")
        if cap_name in self.COUNTERS:
            raise ValueError(f"Counter with name {name} already exists.")
        if self.METER:
            self.COUNTERS[cap_name] = self.METER.create_counter(name=name, 
                                                    description=description)
        else:
            self.COUNTERS[cap_name] = self.dummy_counter(name=name, description=description)
        return cap_name
        
    def _configure_simple_trace(self) -> None:
        print("==============Configuring SIMPLE LTM =============")
        """Configures a smple tracer."""
        resource = Resource(
                attributes={
                    "service.name": cfg.APPLICATION_ACRONYM,
                    "service.version": cfg.VERSION,
                }
            )

        trace.set_tracer_provider(TracerProvider(resource=resource))
        self.TRACER = trace.get_tracer(__name__)
        self.set_std_counters()
        
    def _configure_otel(self) -> None:
        """Configures an OTEL TRACER and METER."""
        print("==============Configuring OTEL LTM =============")
        try:
            resource = Resource(
                attributes={
                    "service.name": cfg.APPLICATION_ACRONYM,
                    "service.version": cfg.VERSION,
                }
            )

            trace.set_tracer_provider(TracerProvider(resource=resource))
            otlp_exporter = OTLPSpanExporter(endpoint=cfg.processing.OLTP.Tracer.endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)

            reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=cfg.processing.OLTP.Metric.endpoint)
            )
            meterprovider = MeterProvider(resource=resource, metric_readers=[reader])
            metrics.set_meter_provider(meterprovider)

            # Create the global Tracer and Meter Object
            # Creates a tracer from the global tracer provider
            self.TRACER = trace.get_tracer(__name__)
            # Creates a meter from the global meter provider
            self.METER = metrics.get_meter(__name__)
        except Exception as e:
            print("Error", e)
            
# Setup Decoraters
class TracingDecoratorOptions:
    class NamingSchemes:
        @staticmethod
        def function_qualified_name(func: Callable):
            return func.__qualname__

        default_scheme = function_qualified_name

    naming_scheme: Callable[[Callable], str] = NamingSchemes.default_scheme
    default_attributes: Dict[str, str] = {}

    @staticmethod
    def set_naming_scheme(naming_scheme: Callable[[Callable], str]):
        TracingDecoratorOptions.naming_scheme = naming_scheme

    @staticmethod
    def set_default_attributes(attributes: Dict[str, str] = None):
        for att in attributes:
            TracingDecoratorOptions.default_attributes[att] = attributes[att]


def instrument(
    _func_or_class=None,
    *,
    span_name: str = "",
    record_exception: bool = True,
    attributes: Dict[str, str] = None,
    existing_tracer: Tracer = None,
    ignore=False
):
    """
    A decorator to instrument a class or function with an OTEL tracing span.
    :param cls: internal, used to specify scope of instrumentation
    :param _func_or_class: The function or span to instrument, this is automatically assigned
    :param span_name: Specify the span name explicitly, rather than use the naming convention.
    This parameter has no effect for class decorators: str
    :param record_exception: Sets whether any exceptions occurring in the span and the stacktrace are recorded
    automatically: bool
    :param attributes:A dictionary of span attributes. These will be automatically added to the span. If defined on a
    class decorator, they will be added to every function span under the class.: dict
    :param existing_tracer: Use a specific tracer instead of creating one :Tracer
    :param ignore: Do not instrument this function, has no effect for class decorators:bool
    :return:The decorator function
    """

    def decorate_class(cls):
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            # Ignore private functions, TODO: maybe make this a setting?
            if not name.startswith("_"):
                if isinstance(inspect.getattr_static(cls, name), staticmethod):
                    setattr(
                        cls,
                        name,
                        staticmethod(
                            instrument(
                                record_exception=record_exception,
                                attributes=attributes,
                                existing_tracer=existing_tracer,
                            )(method)
                        ),
                    )
                else:
                    setattr(
                        cls,
                        name,
                        instrument(
                            record_exception=record_exception,
                            attributes=attributes,
                            existing_tracer=existing_tracer,
                        )(method),
                    )

        return cls

    # Check if this is a span or class decorator
    if inspect.isclass(_func_or_class):
        return decorate_class(_func_or_class)

    def span_decorator(func_or_class):
        if inspect.isclass(func_or_class):
            return decorate_class(func_or_class)

        sig = inspect.signature(func_or_class)

        # Check if already decorated (happens if both class and function
        # decorated). If so, we keep the function decorator settings only
        undecorated_func = getattr(func_or_class, "__tracing_unwrapped__", None)
        if undecorated_func:
            # We have already decorated this function, override
            return func_or_class

        setattr(func_or_class, "__tracing_unwrapped__", func_or_class)

        tracer = existing_tracer or trace.get_tracer(func_or_class.__module__)

        def _set_semantic_attributes(span, func: Callable):
            span.set_attribute(SpanAttributes.CODE_NAMESPACE, func.__module__)
            span.set_attribute(SpanAttributes.CODE_FUNCTION, func.__qualname__)
            span.set_attribute(SpanAttributes.CODE_FILEPATH, func.__code__.co_filename)
            span.set_attribute(SpanAttributes.CODE_LINENO, func.__code__.co_firstlineno)

        def _set_attributes(span, attributes_dict):
            if attributes_dict:
                for att in attributes_dict:
                    span.set_attribute(att, attributes_dict[att])

        @wraps(func_or_class)
        def wrap_with_span_sync(*args, **kwargs):
            name = span_name or TracingDecoratorOptions.naming_scheme(func_or_class)
            with tracer.start_as_current_span(
                name, record_exception=record_exception
            ) as span:
                _set_semantic_attributes(span, func_or_class)
                _set_attributes(span, TracingDecoratorOptions.default_attributes)
                _set_attributes(span, attributes)
                return func_or_class(*args, **kwargs)

        @wraps(func_or_class)
        async def wrap_with_span_async(*args, **kwargs):
            name = span_name or TracingDecoratorOptions.naming_scheme(func_or_class)
            with tracer.start_as_current_span(
                name, record_exception=record_exception
            ) as span:
                _set_semantic_attributes(span, func_or_class)
                _set_attributes(span, TracingDecoratorOptions.default_attributes)
                _set_attributes(span, attributes)
                print(name, "+++++++", kwargs)
                return await func_or_class(*args, **kwargs)

        if ignore:
            return func_or_class
        # print("asyncio.iscoroutinefunction(func_or_class)", asyncio.iscoroutinefunction(func_or_class))
        wrapper = (
            wrap_with_span_async
            if asyncio.iscoroutinefunction(func_or_class)
            else wrap_with_span_sync
        )
        wrapper.__signature__ = inspect.signature(func_or_class)

        return wrapper

    if _func_or_class is None:
        return span_decorator
    else:
        return span_decorator(_func_or_class)
    
# Set the clobal variables
LTM = xxxLTM()
