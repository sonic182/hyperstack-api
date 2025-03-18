import os
from typing import Literal, Optional
from pydantic import BaseModel, Field
from aiosonic.base_client import AioSonicBaseClient


class EnvironmentRequest(BaseModel):
    name: str
    region: Literal["CANADA-1", "NORWAY-1"] = Field(
        description="Region where the environment will be created"
    )


class KeypairRequest(BaseModel):
    name: str
    environment_name: str
    public_key: str = Field(
        description="SSH public key in OpenSSH format"
    )


class VirtualMachineRequest(BaseModel):
    name: str
    environment_name: str
    image_name: str
    create_bootable_volume: bool = False
    flavor_name: str
    key_name: str
    user_data: str = ""
    assign_floating_ip: bool = True
    count: int = 1


class Hyperstack(AioSonicBaseClient):
    base_url = "https://infrahub-api.nexgencloud.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Hyperstack client.
        
        Args:
            api_key: API key for authentication (defaults to HYPERSTACK_KEY env variable)
        
        Raises:
            ValueError: If no API key is provided or found in environment
        """
        self.api_key = api_key or os.environ.get("HYPERSTACK_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set HYPERSTACK_KEY environment variable or pass api_key parameter.")
        
        self.default_headers = {
            'api_key': self.api_key
        }
        super().__init__()

    async def create_environment(self, name: str, region: Literal["CANADA-1", "NORWAY-1"]):
        """
        Create a new environment.
        
        Args:
            name: Name for the environment
            region: Region where the environment will be created
            
        Returns:
            Response containing the created environment details
        """
        data = EnvironmentRequest(name=name, region=region)
        return await self.post("/core/environments", json=data.model_dump())

    async def create_keypair(self, name: str, environment_name: str, public_key: str):
        """
        Create a new keypair.
        
        Args:
            name: Name for the keypair
            environment_name: Name of the environment
            public_key: SSH public key in OpenSSH format
            
        Returns:
            Response containing the created keypair details
        """
        data = KeypairRequest(
            name=name,
            environment_name=environment_name,
            public_key=public_key
        )
        return await self.post("/core/keypairs", json=data.model_dump())
          
    async def get_flavors(self):
        """
        Fetch available instance flavors.
        
        Returns:
            Response containing the list of available flavors.
        """
        return await self.get("/core/flavors")

    async def get_images(self):
        """
        Fetch available system images.
        
        Returns:
            Response containing the list of available images.
        """
        return await self.get("/core/images")

    async def list_virtual_machines(
        self,
        search: Optional[str] = None,
        environment: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ):
        """
        Fetch a list of virtual machines with optional filtering.
        
        Args:
            search: Search for virtual machines by name or ID
            environment: Filter by environment name or ID
            page: Page number to retrieve
            page_size: Number of virtual machines per page
            
        Returns:
            Response containing the list of virtual machines with their details
        """
        params = {}
        if search:
            params["search"] = search
        if environment:
            params["environment"] = environment
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size
            
        return await self.get("/core/virtual-machines", params=params)

    async def get_virtual_machine(self, vm_id: str):
        """
        Fetch details of a specific virtual machine by ID.
        
        Args:
            vm_id: The ID of the virtual machine to retrieve
            
        Returns:
            Response containing the virtual machine details
        """
        return await self.get(f"/core/virtual-machines/{vm_id}")

    async def create_virtual_machine(
        self,
        name: str,
        environment_name: str,
        image_name: str,
        flavor_name: str,
        key_name: str,
        count: int,
        assign_floating_ip: bool = True,
        create_bootable_volume: bool = False,
        user_data: str = ""
    ):
        """
        Create a new virtual machine.
        
        Args:
            name: Name for the virtual machine (max 50 characters)
            environment_name: Name of the environment
            image_name: Name of the image to use
            flavor_name: Name of the flavor (instance type) to use
            key_name: Name of the keypair to use
            count: Number of instances to create
            assign_floating_ip: Whether to assign a floating IP (public accessibility)
            create_bootable_volume: Whether to create a bootable volume
            user_data: Optional user data for cloud-init
            
        Returns:
            Response containing the created virtual machine details
        """
        data = VirtualMachineRequest(
            name=name,
            environment_name=environment_name,
            image_name=image_name,
            flavor_name=flavor_name,
            key_name=key_name,
            count=count,
            assign_floating_ip=assign_floating_ip,
            create_bootable_volume=create_bootable_volume,
            user_data=user_data
        )
        return await self.post("/core/virtual-machines", json=data.model_dump())

    async def start_virtual_machine(self, vm_id: str):
        """
        Start a virtual machine.
        
        Args:
            vm_id: The ID of the virtual machine to start
            
        Returns:
            Response confirming the virtual machine has been started
        """
        return await self.get(f"/core/virtual-machines/{vm_id}/start")

    async def stop_virtual_machine(self, vm_id: str):
        """
        Stop (shut down) a virtual machine.
        
        Args:
            vm_id: The ID of the virtual machine to stop
            
        Returns:
            Response confirming the virtual machine has been stopped
        """
        return await self.get(f"/core/virtual-machines/{vm_id}/stop")

    async def hard_reboot_virtual_machine(self, vm_id: str):
        """
        Hard-reboot a virtual machine.
        
        Args:
            vm_id: The ID of the virtual machine to reboot
            
        Returns:
            Response confirming the virtual machine has been rebooted
        """
        return await self.get(f"/core/virtual-machines/{vm_id}/hard-reboot")

    async def hibernate_virtual_machine(self, vm_id: str):
        """
        Hibernate a virtual machine.
        
        Args:
            vm_id: The ID of the virtual machine to hibernate
            
        Returns:
            Response confirming the virtual machine hibernation has been initiated
        """
        return await self.get(f"/core/virtual-machines/{vm_id}/hibernate")

    async def restore_hibernated_virtual_machine(self, vm_id: str):
        """
        Restore a virtual machine from hibernation.
        
        Args:
            vm_id: The ID of the hibernated virtual machine to restore
            
        Returns:
            Response confirming the virtual machine has been restored from hibernation
        """
        return await self.get(f"/core/virtual-machines/{vm_id}/hibernate-restore")

    async def delete_virtual_machine(self, vm_id: str):
        """
        Permanently delete a virtual machine.
        
        Args:
            vm_id: The ID of the virtual machine to delete
            
        Returns:
            Response confirming the virtual machine has been deleted
        """
        return await self.delete(f"/core/virtual-machines/{vm_id}")
