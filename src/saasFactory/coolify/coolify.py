from coolipy import Coolipy
#from coolipy import Coolipy
#from coolipy.models.service import ServiceModelCreate, ServiceModel



class CoolifyClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def connect(self):
        """
        Grabs Coolify configuration from the user's YAML file. Then creates a Coolify client object.
        """
        

#figure out  not having coolipy recognized as a module

#start by creating a deployment key, then prompting the user to add it to their github repo, 
#  then creating a project from dockerfile with dev and prod envs 
#  then see about creating a base next repo with the correct configs for deployment that can be forked 
#  try to use the github cli to do all of this or the github api rather than using the web interface


coolify = Coolipy(
    coolify_api_key="1|xxVkgm984L1ufDSiqfKNxghcS38hnScBsTuFgUXGc1ec17db",
    coolify_endpoint="coolify.agents4biz.com",
    omit_port=True,
    http_protocol="https"
)
res = coolify.services.list()
print(res.data)