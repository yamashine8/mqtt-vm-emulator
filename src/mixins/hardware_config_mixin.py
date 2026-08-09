import random
import uuid

class HardwareConfigMixin:
    @staticmethod
    def generate_mac():
        return ":".join(
            f"{random.randint(0, 255):02x}"
            for _ in range(6)
        )


    def get_config(self):
        return {
            "vm_id": f"vm-{uuid.uuid4().hex[:8]}",
            "name": "vm-web-01",
            "hostname": "host-01",
            "os": "linux",
            "os_version": "Ubuntu 24.04",
            "status": "running",
            "hardware": {
                "cpu": {
                    "cores": 8,
                },
                "memory": {
                    "total_mb": 16384,
                },
                "disk": {
                    "total_gb": 500,
                },
            },
            "network": {
                "ip": f"10.10.{random.randint(0, 255)}.{random.randint(1, 254)}",
                "mac": self.generate_mac(),
            },
            "infrastructure": {
                "host": "esxi-03",
                "cluster": "cluster-2",
                "datastore": "datastore-4"
            },
            "metadata": {
                "environment": f"{random.choice(["dev", "prod", "service"])}",
                "project": "backend",
                "owner": f"team-{random.choice(["1233waa", "eqw33", "33311ddddd"])}"
            }
        }

