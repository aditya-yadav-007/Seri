import serial
import threading
import argparse
import os
import sys
from datetime import datetime
from serial.tools import list_ports
from rich import print  # If not installed: pip install rich

# Global serial object
ser = None
log_file = open("serial_log.txt", "a")

def list_serial_ports():
    ports = list_ports.comports()
    if not ports:
        print("[red]No serial ports found.[/red]")
        sys.exit(1)
    print("[bold yellow]Available COM Ports:[/bold yellow]")
    for i, port in enumerate(ports):
        print(f" [{i}] {port.device} - {port.description}")
    choice = input("Select port by number: ")
    try:
        return ports[int(choice)].device
    except (ValueError, IndexError):
        print("[red]Invalid choice. Exiting.[/red]")
        sys.exit(1)

def setup_serial(port, baud):
    global ser
    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"[green]Connected to {port} at {baud} baud.[/green]")
    except serial.SerialException as e:
        print(f"[red]Error opening serial port: {e}[/red]")
        sys.exit(1)

def read_from_serial():
    while True:
        try:
            if ser.in_waiting:
                line = ser.readline().decode(errors='ignore').strip()
                if line:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    msg = f"[{timestamp}] [cyan]{line}[/cyan]"
                    print(f"\n{msg}")
                    log_file.write(f"{timestamp} {line}\n")
                    log_file.flush()
        except Exception as e:
            print(f"[red]Read error: {e}[/red]")
            break

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    parser = argparse.ArgumentParser(description="Advanced Serial Terminal")
    parser.add_argument('--port', help="Serial port (e.g., COM3, /dev/ttyUSB0)")
    parser.add_argument('--baud', type=int, default=9600, help="Baud rate (default 9600)")
    args = parser.parse_args()

    port = args.port if args.port else list_serial_ports()
    setup_serial(port, args.baud)

    clear_screen()
    print("[bold green]Serial Terminal Ready.[/bold green]")
    print("[dim]Type 'exit' or press Ctrl+C to quit.[/dim]\n")

    threading.Thread(target=read_from_serial, daemon=True).start()

    try:
        while True:
            msg = input("> ").strip()
            if msg.lower() in ['exit', 'quit']:
                break
            try:
                ser.write((msg + '\n').encode('utf-8'))
            except UnicodeEncodeError:
                print("[red]Cannot send message due to encoding issue.[/red]")
    except KeyboardInterrupt:
        print("\n[yellow]User interrupted.[/yellow]")
    finally:
        print("[blue]Closing serial port...[/blue]")
        if ser:
            ser.close()
        log_file.close()

if __name__ == "__main__":
    main()
