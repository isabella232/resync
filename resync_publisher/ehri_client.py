'''
Created on 24 sep. 2015

@author: linda
'''
from resync.client import Client
from resync.change_list import ChangeList


class ResourceSyncPublisherClient(Client):
    '''
    ResourceSyncPublisherClient
    '''

    def __init__(self, checksum=False, verbose=False, dryrun=False):
        '''
        Constructor
        '''
        super(ResourceSyncPublisherClient, self).__init__(checksum, verbose, dryrun)

    def calculate_changelist(self, paths=None, outfile=None,
                             resource_sitemap=None, changelist_sitemap=None,
                             links=None):
        """ Build a ChangeList describing the updated/new files on local disk
        Based on the combined set of the referenced ResourceList, ChangeList
        and the local files.
        """
        # create fresh resourcelist, the combination of
        old_rl = self.read_reference_resource_list(resource_sitemap)
        cl = ChangeList()
        cl.mapper = self.mapper
        cl.read(uri=changelist_sitemap, index_only=(not self.allow_multifile))
        for r in cl.resources:
            if(r.change == 'deleted'):
                old_rl.remove(r)
            else:
                r.change = None
                old_rl.add(r, True)
        combined_rl = old_rl
        # update resourcelist
        # Build a new Resource List from the files on local disk
        new_rl = self.build_resource_list(paths=paths, set_path=None)
        (_, updated, _, created) = combined_rl.compare(new_rl)
        combined_rl.add(updated, True)
        combined_rl.add(created, True)
        # compare resourcelists
        old_rl = self.read_reference_resource_list(resource_sitemap)
        cl = ChangeList(ln=links)
        (_, updated, deleted, created) = old_rl.compare(combined_rl)
        cl.add_changed_resources(updated, change='updated')
        cl.add_changed_resources(deleted, change='deleted')
        cl.add_changed_resources(created, change='created')
        # 4. Write out change list
        cl.mapper = self.mapper
        cl.pretty_xml = self.pretty_xml
        if (self.max_sitemap_entries is not None):
            cl.max_sitemap_entries = self.max_sitemap_entries
        if (outfile is None):
            print(cl.as_xml())
        else:
            cl.write(basename=outfile)
        return(cl)
