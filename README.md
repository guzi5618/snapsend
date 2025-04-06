# Snap Send

A simple tool for transferring files between mobile and desktop on the same local network.

## Features

- Local network file transfer without internet connection
- Files expire after 5 minutes with countdown timer
- Two-way file transfers (mobile ↔ desktop)

<div align="center">
  <img src="screenshots/desktop_view.jpg" width="450" alt="Desktop view">
  <p><em>Desktop view with QR code for mobile connection</em></p>

  <img src="screenshots/mobile_view.jpg" width="300" alt="Mobile view">
  <p><em>Mobile view of Snap Send</em></p>
</div>

## Setup

1. Make sure you have Python 3 installed on your computer (built-in on most Mac systems)
2. Clone this repository or download the files
3. Open a terminal in the project directory
4. Run the server:

```bash
python3 snap_send_server.py
```

5. A browser window will automatically open with the desktop interface
6. Scan the QR code with your mobile device
7. Upload files from your mobile device to your computer 


## Troubleshooting

- **Can't connect from mobile**: Make sure both devices are on the same network
- **QR code not scanning**: Try entering the URL manually on your mobile device
- **Files not transferring**: Check for firewall restrictions on your computer
- **Large files**: Files over 10MB are not supported in this version, but can be set up

## Limitations

This is a simple implementation for local network file transfers. For security reasons:

- No encryption is used (don't transfer sensitive data)
- Transfers work only on the same local network
- There's no authentication mechanism
- All files are automatically deleted after 5 minutes

## License

MIT 