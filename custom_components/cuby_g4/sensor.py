from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_STATE

class CubyG4Sensor(SensorEntity):
  """Cuby G4 Sensor."""

  def __init__(self, config: ConfigEntry):
    super().__init__(config)
    self._name = config.get("name")
    self._host = config.get("host")
    self._port = config.get("port")
    self._username = config.get("username")
    self._password = config.get("password")

  @property
  def name(self):
    return self._name

  def _get_token(self):
    """Get the access token to the Cuby Cloud API."""
    try:
      with requests.Session() as session:
        response = session.post(
          f"https://cuby.cloud/api/v2/auth/token",
          json={"username": self._username, "password": self._password},
        )
        response.raise_for_status()
        data = response.json()

        return data["token"]
    except requests.exceptions.HTTPError as error:
      self.logger.error("Error getting access token: %s", error)
      return None

  @property
  def state(self):
    """Return the state of the sensor."""
    try:
      token = self._get_token()

      if token is None:
        return None

      with requests.Session() as session:
        session.headers["Authorization"] = f"Bearer {token}"
        response = session.get(f"https://cuby.cloud/api/v2/devices/status")
        response.raise_for_status()
        data = response.json()

        return data["state"]
    except requests.exceptions.HTTPError as error:
      self.logger.error("Error connecting to Cuby Cloud: %s", error)
      return None

  @property
  def unit_of_measurement(self):
    """Return the unit of measurement."""
    return "°C"

  @property
  def device_info(self):
    return {
      "identifiers": {(DOMAIN, self._name)},
      "name": self._name,
      "manufacturer": "Cuby",
      "model": "G4",
    }
