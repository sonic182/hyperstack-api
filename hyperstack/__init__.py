import os
from typing import Literal, Optional, Union

from aiosonic.base_client import AioSonicBaseClient
from pydantic import BaseModel, Field, field_validator


class EnvironmentRequest(BaseModel):
    name: str
    region: Literal["CANADA-1", "NORWAY-1"] = Field(
        description="Region where the environment will be created"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Environment name cannot be empty")
        return v.strip()


class KeypairRequest(BaseModel):
    name: str
    environment_name: str
    public_key: str = Field(description="SSH public key in OpenSSH format")

    @field_validator("name", "environment_name")
    @classmethod
    def validate_names(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name fields cannot be empty")
        return v.strip()

    @field_validator("public_key")
    @classmethod
    def validate_public_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Public key cannot be empty")
        if not v.startswith(("ssh-rsa", "ssh-ed25519", "ecdsa-sha2-nistp")):
            raise ValueError("Public key must be in OpenSSH format")
        return v.strip()


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

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Machine name cannot be empty")
        if len(v) > 50:
            raise ValueError("Machine name cannot exceed 50 characters")
        return v.strip()

    @field_validator("environment_name", "image_name", "flavor_name", "key_name")
    @classmethod
    def validate_resource_names(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Resource name fields cannot be empty")
        return v.strip()

    @field_validator("count")
    @classmethod
    def validate_count(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Count must be at least 1")
        return v


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
            raise ValueError(
                "API key is required. Set HYPERSTACK_KEY environment variable or pass api_key parameter."
            )

        self.default_headers = {"api_key": self.api_key}
        super().__init__()

    async def get_environment(self, environment_id: str) -> Union[dict, str]:
        """
        Fetch details of a specific environment by ID.

        Args:
            environment_id: The ID of the environment to retrieve

        Returns:
            Response containing the environment details

        Raises:
            ValueError: If environment_id is empty
        """
        if not environment_id or not environment_id.strip():
            raise ValueError("Environment ID cannot be empty")

        return await self.get(f"/core/environments/{environment_id.strip()}")

    async def list_environments(
        self,
        search: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Union[dict, str]:
        """
        Fetch a list of environments with optional filtering.

        Args:
            search: Search for environments by name, ID, or region
            page: Page number to retrieve
            page_size: Number of environments per page

        Returns:
            Response containing the list of environments with their details

        Raises:
            ValueError: If page or page_size are negative
        """
        params = {}

        if search is not None:
            if search.strip():
                params["search"] = search.strip()

        if page is not None:
            if page < 0:
                raise ValueError("Page number cannot be negative")
            params["page"] = page

        if page_size is not None:
            if page_size < 1:
                raise ValueError("Page size must be at least 1")
            params["pageSize"] = page_size

        return await self.get("/core/environments", params=params)

    async def create_environment(
        self, name: str, region: Literal["CANADA-1", "NORWAY-1"]
    ) -> Union[dict, str]:
        """
        Create a new environment.

        Args:
            name: Name for the environment
            region: Region where the environment will be created

        Returns:
            Response containing the created environment details

        Raises:
            ValueError: If validation fails for any field
        """
        data = EnvironmentRequest(name=name, region=region)
        return await self.post("/core/environments", json=data.model_dump())

    async def update_environment(
        self, environment_id: str, new_name: str
    ) -> Union[dict, str]:
        """
        Update the name of an existing environment.

        Args:
            environment_id: ID of the environment to update
            new_name: New name for the environment (max 50 characters)

        Returns:
            Response containing the updated environment details

        Raises:
            ValueError: If environment_id is empty or new_name is invalid
        """
        if not environment_id or not environment_id.strip():
            raise ValueError("Environment ID cannot be empty")

        environment_id = environment_id.strip()

        if not new_name or not new_name.strip():
            raise ValueError("Environment name cannot be empty")

        new_name = new_name.strip()
        if len(new_name) > 50:
            raise ValueError("Environment name cannot exceed 50 characters")

        data = {"name": new_name}
        return await self.put(f"/core/environments/{environment_id}", json=data)

    async def delete_environment(self, environment_id: str) -> Union[dict, str]:
        """
        Permanently delete an environment.

        Args:
            environment_id: The ID of the environment to delete

        Returns:
            Response confirming the environment has been deleted

        Raises:
            ValueError: If environment_id is empty
        """
        if not environment_id or not environment_id.strip():
            raise ValueError("Environment ID cannot be empty")

        return await self.delete(f"/core/environments/{environment_id.strip()}")

    async def create_keypair(
        self, name: str, environment_name: str, public_key: str
    ) -> Union[dict, str]:
        """
        Create a new keypair.

        Args:
            name: Name for the keypair
            environment_name: Name of the environment
            public_key: SSH public key in OpenSSH format

        Returns:
            Response containing the created keypair details

        Raises:
            ValueError: If validation fails for any field
        """
        data = KeypairRequest(
            name=name, environment_name=environment_name, public_key=public_key
        )
        return await self.post("/core/keypairs", json=data.model_dump())

    async def get_flavors(self) -> Union[dict, str]:
        """
        Fetch available instance flavors.

        Returns:
            Response containing the list of available flavors.
        """
        return await self.get("/core/flavors")

    async def get_images(
        self,
        region: Optional[str] = None,
        include_public: Optional[bool] = None,
        search: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Union[dict, str]:
        """
        Fetch available system images with optional filtering.

        Args:
            region: Filter images by region name
            include_public: Whether to include public images (defaults to false if not specified)
            search: Search for images by name
            page: Page number to retrieve
            per_page: Number of images per page

        Returns:
            Response containing the list of available images matching the criteria

        Raises:
            ValueError: If page or per_page are negative
        """
        params = {}

        if region is not None:
            if region.strip():
                params["region"] = region.strip()

        if include_public is not None:
            params["include_public"] = include_public

        if search is not None:
            if search.strip():
                params["search"] = search.strip()

        if page is not None:
            if page < 0:
                raise ValueError("Page number cannot be negative")
            params["page"] = page

        if per_page is not None:
            if per_page < 1:
                raise ValueError("Per page value must be at least 1")
            params["per_page"] = per_page

        return await self.get("/core/images", params=params)

    async def get_gpu_stocks(self) -> Union[dict, str]:
        """
        Fetch information on current and upcoming GPU availability.
        
        Returns:
            Response containing information on GPU stocks organized by region and GPU model.
            
        Details:
            This endpoint returns details about the current availability of GPUs and upcoming
            restocking information across different regions and GPU models.
        """
        return await self.get("/core/stocks")

    async def list_virtual_machines(
        self,
        search: Optional[str] = None,
        environment: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Union[dict, str]:
        """
        Fetch a list of virtual machines with optional filtering.

        Args:
            search: Search for virtual machines by name or ID
            environment: Filter by environment name or ID
            page: Page number to retrieve
            page_size: Number of virtual machines per page

        Returns:
            Response containing the list of virtual machines with their details

        Raises:
            ValueError: If page or page_size are negative
        """
        params = {}

        if search is not None:
            if search.strip():
                params["search"] = search.strip()

        if environment is not None:
            if environment.strip():
                params["environment"] = environment.strip()

        if page is not None:
            if page < 0:
                raise ValueError("Page number cannot be negative")
            params["page"] = page

        if page_size is not None:
            if page_size < 1:
                raise ValueError("Page size must be at least 1")
            params["pageSize"] = page_size

        return await self.get("/core/virtual-machines", params=params)

    async def get_virtual_machine(self, vm_id: str) -> Union[dict, str]:
        """
        Fetch details of a specific virtual machine by ID.

        Args:
            vm_id: The ID of the virtual machine to retrieve

        Returns:
            Response containing the virtual machine details

        Raises:
            ValueError: If vm_id is empty
        """
        if not vm_id or not vm_id.strip():
            raise ValueError("Virtual machine ID cannot be empty")

        return await self.get(f"/core/virtual-machines/{vm_id.strip()}")

    async def create_virtual_machine(
        self,
        name: str,
        environment_name: str,
        image_name: str,
        flavor_name: str,
        key_name: str,
        count: int = 1,
        assign_floating_ip: bool = True,
        create_bootable_volume: bool = False,
        user_data: str = "",
    ) -> Union[dict, str]:
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

        Raises:
            ValueError: If validation fails for any field
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
            user_data=user_data,
        )
        return await self.post("/core/virtual-machines", json=data.model_dump())

    async def _execute_vm_action(self, vm_id: str, action: str) -> Union[dict, str]:
        """
        Execute an action on a virtual machine.

        Args:
            vm_id: The ID of the virtual machine
            action: The action to execute

        Returns:
            Response from the API

        Raises:
            ValueError: If vm_id is empty
        """
        if not vm_id or not vm_id.strip():
            raise ValueError("Virtual machine ID cannot be empty")

        return await self.get(f"/core/virtual-machines/{vm_id.strip()}/{action}")

    async def start_virtual_machine(self, vm_id: str) -> Union[dict, str]:
        """
        Start a virtual machine.

        Args:
            vm_id: The ID of the virtual machine to start

        Returns:
            Response confirming the virtual machine has been started

        Raises:
            ValueError: If vm_id is empty
        """
        return await self._execute_vm_action(vm_id, "start")

    async def stop_virtual_machine(self, vm_id: str) -> Union[dict, str]:
        """
        Stop (shut down) a virtual machine.

        Args:
            vm_id: The ID of the virtual machine to stop

        Returns:
            Response confirming the virtual machine has been stopped

        Raises:
            ValueError: If vm_id is empty
        """
        return await self._execute_vm_action(vm_id, "stop")

    async def hard_reboot_virtual_machine(self, vm_id: str) -> Union[dict, str]:
        """
        Hard-reboot a virtual machine.

        Args:
            vm_id: The ID of the virtual machine to reboot

        Returns:
            Response confirming the virtual machine has been rebooted

        Raises:
            ValueError: If vm_id is empty
        """
        return await self._execute_vm_action(vm_id, "hard-reboot")

    async def hibernate_virtual_machine(self, vm_id: str) -> Union[dict, str]:
        """
        Hibernate a virtual machine.

        Args:
            vm_id: The ID of the virtual machine to hibernate

        Returns:
            Response confirming the virtual machine hibernation has been initiated

        Raises:
            ValueError: If vm_id is empty
        """
        return await self._execute_vm_action(vm_id, "hibernate")

    async def restore_hibernated_virtual_machine(self, vm_id: str) -> Union[dict, str]:
        """
        Restore a virtual machine from hibernation.

        Args:
            vm_id: The ID of the hibernated virtual machine to restore

        Returns:
            Response confirming the virtual machine has been restored from hibernation

        Raises:
            ValueError: If vm_id is empty
        """
        return await self._execute_vm_action(vm_id, "hibernate-restore")

    async def delete_virtual_machine(self, vm_id: str) -> Union[dict, str]:
        """
        Permanently delete a virtual machine.

        Args:
            vm_id: The ID of the virtual machine to delete

        Returns:
            Response confirming the virtual machine has been deleted

        Raises:
            ValueError: If vm_id is empty
        """
        if not vm_id or not vm_id.strip():
            raise ValueError("Virtual machine ID cannot be empty")

        return await self.delete(f"/core/virtual-machines/{vm_id.strip()}")
