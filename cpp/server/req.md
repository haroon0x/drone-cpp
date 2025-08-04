# Base Station Server Requirements

Any server implementation, regardless of the programming language or framework used, must meet the following requirements to be compatible with the `drone_client`.

### 1. Network Protocol

The server **must** be a **TCP server**. The drone client uses a reliable, connection-oriented TCP socket (`SOCK_STREAM`) to communicate.

### 2. Listening Address

The server must listen on the specific IP address and port that the drone client is configured to connect to. This is defined in the drone client's `config.conf` file.

### 3. Incoming Data Format

The server must be able to receive and parse a JSON message with the following exact structure and fields:

```json
{
    "message_type": "gps_coordinates",
    "timestamp": 1674123456789,
    "latitude": 47.39774200,
    "longitude": 8.54559400,
    "altitude": 123.45
}
```

- `message_type`: A string (always `"gps_coordinates"`).
- `timestamp`: A large integer representing the milliseconds since the Unix epoch.
- `latitude`: A floating-point number.
- `longitude`: A floating-point number.
- `altitude`: A floating-point number.

### 4. Acknowledgment Response

After successfully receiving and parsing the data, the server should send a response back to the client to confirm receipt. The drone client waits for this acknowledgment to complete the communication loop.

The response can be a simple JSON object, for example:

```json
{
    "status": "success"
}
```
