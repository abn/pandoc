
# Python 2.7 Standard Library
import collections

# Third-Party Libraries
import pkg_resources

# Pandoc
import pandoc.utils

# Haskell Primitives & Containers
# ------------------------------------------------------------------------------
Bool = bool
Double = float
Int = int
String = unicode
list = list
tuple = tuple
map = type("map", (collections.OrderedDict,), {})

# Haskell Type Constructs
# ------------------------------------------------------------------------------
def _fail_init(self, *args, **kwargs):
    type_name = type(self).__name__
    error = "cannot instantiate abstract type {type}"
    raise NotImplementedError(error.format(type=type_name))

class Type(object):
    __init__ = _fail_init

class Data(Type):
    pass

class Constructor(Data):
    def __init__(self, *args):
        if type(self) is Constructor:
            _fail_init(self, *args)
        else:
            self.args = args
    def __repr__(self):
        typename = type(self).__name__
        args = ", ".join(repr(arg) for arg in self.args)
        return "{0}({1})".format(typename, args)
    __str__ = __repr__

class TypeDef(Type):
    pass
    

# Pandoc Types
# ------------------------------------------------------------------------------
def make_types(defs=None):
    types_dict = globals()
    if defs is None:
        defs_src = pkg_resources.resource_string("pandoc", "Definition.hs")
        defs = pandoc.utils.parse(defs_src)
    for decl in defs:
        decl_type = decl[0]
        type_name = decl[1][0]
        if decl_type in ("data", "newtype"):
            data_type = type(type_name, (Data,), {"_def": decl})
            types_dict[type_name] = data_type
            # Remark: when there is a constructor with the same name as its
            #         data type, the data type is shadowed. 
            #         This is intentional, but it's only consistent because 
            #         it happens when there is a single constructor. 
            # TODO: add an assert / check for this condition.
            for constructor in decl[1][1]:
                constructor_name = constructor[0]
                bases = (Constructor, data_type)
                type_ = type(constructor_name, bases, {"_def": constructor})
                types_dict[constructor_name] = type_
        elif decl_type == "type":
            type_ = type(type_name, (TypeDef,), {"_def": decl})
            types_dict[type_name] =type_
        
make_types()
