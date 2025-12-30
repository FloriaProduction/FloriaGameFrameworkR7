import typing as t
from abc import abstractmethod, ABC, ABCMeta

from .... import Types, Abc, Validator
from . import Components as C


class ShaderConstuctMeta(ABCMeta):
    def __new__(
        mcls: type,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, t.Any],
        /,
        **kw: t.Any,
    ) -> type:
        if sum(1 if issubclass(base, ShaderConstuct) else 0 for base in bases) > 1:
            raise ValueError()

        layout_index: int = 0
        for base in bases:
            if not issubclass(base, ShaderConstuct):
                continue
            layout_index = base.__layout_index  # pyright: ignore[reportPrivateUsage]
            break

        for varname, var in (item for item in namespace.items() if isinstance(item[1], C.Component)):
            if isinstance(var, C.ComponentNamed) and var.name is None:
                var.name = varname

            if isinstance(var, C.Attrib):
                var.index = layout_index

                if var.type == 'mat3':
                    layout_index += 3
                elif var.type == 'mat4':
                    layout_index += 4
                else:
                    layout_index += 1

        cls = t.cast(type, super().__new__(mcls, name, bases, namespace, **kw))  # pyright: ignore[reportCallIssue]

        cls.__layout_index = layout_index

        return cls


class ShaderConstuct(metaclass=ShaderConstuctMeta):
    __layout_index: int = 0
    __source: t.Optional[str] = None
    __scheme: t.Optional[Abc.Graphic.ShaderPrograms.Scheme] = None

    @classmethod
    def BuildSource(cls) -> str:
        version: t.Optional[C.ContexVersion] = None

        attribs: set[C.Attrib] = set()
        uniforms: set[C.Uniform] = set()
        pastes: set[C.Paste] = set()
        params: set[C.Param] = set()
        functions: set[C.Function] = set()

        main: t.Optional[C.Main] = None

        for varname, var in (
            item  #
            for base in cls.mro()[::-1]
            if base is not object
            for item in base.__dict__.items()
            if isinstance(item[1], C.Component)
        ):
            if isinstance(var, C.ContexVersion):
                version = var

            elif isinstance(var, C.Param):
                params.add(var)

            elif isinstance(var, C.Attrib):
                attribs.add(var)

            elif isinstance(var, C.Uniform):
                uniforms.add(var)

            elif isinstance(var, C.Function):
                if isinstance(var, C.Main):
                    main = var

                else:
                    functions.add(var)

            elif isinstance(var, C.Paste):
                pastes.add(var)

            else:
                raise ValueError(varname, var)

        if version is None:
            version = C.ContexVersion(420, 'core')

        if main is None:
            raise ValueError()

        attribs_source: list[str] = []
        for attrib in attribs:
            attribs_source.append(
                f'layout(location = {Validator.NotNone(attrib.index)}) in {attrib.type} {Validator.NotNone(attrib.name)};'
            )

        uniforms_source: list[str] = []
        for unfirom in uniforms:
            uniforms_source.append(
                f'uniform {unfirom.type} {unfirom.name}{f' = {unfirom.value}' if unfirom.value is not None else ''};'
            )

        functions_source: list[str] = []
        for func in functions:
            functions_source.append(func.source)

        params_source: list[str] = []
        for param in params:
            params_source.append(
                f'{'flat' if param.type in ('int', 'uint') else ''} {param.direction} {param.type} {param.name};'
            )

        paste_source: list[str] = []
        for paste in pastes:
            paste_source.append(paste.source)

        source = f'''
            {version.source}

            {'\n'.join(attribs_source)}

            {'\n'.join(uniforms_source)}
        
            {'\n'.join(params_source)}

            {'\n'.join(functions_source)}
            
            {'\n'.join(paste_source)}

            {main.source}
        '''

        return source

    @classmethod
    def BuildScheme(cls):
        scheme_base: dict[int, Abc.Graphic.ShaderPrograms.SchemeItem] = {}
        scheme_instance: dict[int, Abc.Graphic.ShaderPrograms.SchemeItem] = {}

        for _, var in (
            item  #
            for base in cls.mro()[::-1]
            if base is not object
            for item in base.__dict__.items()
            if isinstance(item[1], C.Component)
        ):
            if isinstance(var, C.Attrib):
                index = Validator.NotNone(var.index)
                name = Validator.NotNone(var.name)

                if var.instanced:
                    scheme_instance[index] = Abc.Graphic.ShaderPrograms.SchemeItem(
                        attrib=name,
                        type=var.type,
                    )
                else:
                    scheme_base[index] = Abc.Graphic.ShaderPrograms.SchemeItem(
                        attrib=name,
                        type=var.type,
                    )

        scheme_kwargs: dict[
            t.Literal['base', 'instance'],
            dict[int, Abc.Graphic.ShaderPrograms.SchemeItem],
        ] = {}

        scheme_kwargs['base'] = scheme_base
        if len(scheme_instance) > 0:
            scheme_kwargs['instance'] = scheme_instance

        return Abc.Graphic.ShaderPrograms.Scheme(**scheme_kwargs)

    @classmethod
    def GetSource(cls, rebuild: bool = False) -> str:
        if cls.__source is None or rebuild:
            cls.__source = cls.BuildSource()
        return cls.__source

    @classmethod
    def GetScheme(cls, rebuild: bool = False) -> Abc.Graphic.ShaderPrograms.Scheme:
        if cls.__scheme is None or rebuild:
            cls.__scheme = cls.BuildScheme()
        return cls.__scheme
