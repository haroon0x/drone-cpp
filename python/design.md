Person-Centered GPS Location Tracking via Drone


- **Detects a person** using an external YOLOv8 model
- **Centers** the person in the camera frame by adjusting the drone's **horizontal position** only (no altitude change)
- Once centered, **fetches the GPS coordinates** of the drone's position
- **Transmits coordinates to base station** (with local storage as backup)


### Key Parameters
- **Frame dimensions:** 640x480 pixels
- **Centering threshold:** ±10 pixels
- **Movement velocity:** Proportional to offset (max 2 m/s)
- **GPS precision:** 6 decimal places minimum

### Communication Protocol
- **Base Station Interface:** TCP/UDP socket or MAVLink protocol
- **Message Format:** JSON or custom binary format
- **Retry Logic:** 3 attempts with exponential backoff
- **Fallback:** Local storage if transmission fails

---

## 🎯 Success Criteria

1. **Detection Accuracy:** Person successfully detected and tracked
2. **Centering Precision:** Person centered within ±10 pixel threshold
3. **GPS Accuracy:** Coordinates captured with <3m accuracy
4. **Transmission Reliability:** >95% successful transmission rate
5. **Response Time:** Complete cycle (detect → center → transmit) <5 seconds

