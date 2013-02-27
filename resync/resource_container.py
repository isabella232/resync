"""ResourceSync Resource Container object

All documents in ResourceSync have the same types of information:
they have some top-level metadata and links, and then a list of
resources, each of which may also have metadata and links. This 
class implements this model.

This is a base class for the ListBase class which is in turn the
base class for ResourceList, ChangeList, etc. This class provides
only the data storage and manipulation, ListBase adds IO.
"""
import collections
from w3c_datetime import datetime_to_str

class ResourceContainer(object):
    """Class containing resource-like objects

    Core functionality::
    - resources property that is the set/list of resources
    -- add() to add a resource-like object to self.resources
    -- iter() to get iterator over self.resource in appropriate order
    - md property that is a dict of metadata
    - ln property that is a list of links

    Derived classes may add extra functionality such as len() etc..
    However, any code designed to work with any ResourceContainer
    should use only the core functionality.
    """

    def __init__(self, resources=None, md=None, ln=None):
        self.resources=(resources if (resources is not None) else list())
        self.md=(md if (md is not None) else {})
        self.ln=(ln if (ln is not None) else [])
        self.capability_name=None
        self.capability_md=None

    def __iter__(self):
        """Iterator over all the resources in this resource_list

        Baseline implementation use iterator given by resources property
        """
        return(iter(self.resources))

    @property
    def capability(self):
        return(self.md['capability'])

    @capability.setter
    def capability(self,capability):
        """Get/set the capability attribute of this resource container"""
        self.md['capability']=capability

    def default_capability_and_modified(self):
        """Set capability name and modified time in md

        Every ResourceSync document should have these two top-level
        metadata attributes.
        """
        if ('capability' not in self.md and self.capability_md is not None):
            self.md['capability']=self.capability_md
        if ('modified' not in self.md):
            self.md['modified']=datetime_to_str(no_fractions=True)

    def add(self, resource):
        """Add a resource or an iterable collection of resources to this container

        Must be implemented in derived class
        """
        if isinstance(resource, collections.Iterable):
            for r in resource:
                self.resources.append(r)
        else:
            self.resources.append(resource)

    def uris(self):
        """Return list of all URIs, possibly including dupes"""
        uris = []
        for r in self.resources:
            uris.append(r.uri)
        return(uris)

    def __str__(self):
        """Return string of all resources in order given by interator"""
        s = ''
        for resource in self:
            s += str(resource) + "\n"
        return(s)
