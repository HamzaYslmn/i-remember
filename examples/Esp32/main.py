import tkinter as tk
from tkinter import messagebox
import urllib.request
import urllib.parse
import json
import asyncio

API_URL = "https://i-remember.onrender.com/api/i-remember"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXJpZmllZCI6dHJ1ZSwiZXhwIjo0MzQ4NTYyNTE1LCJkYXRhIjoiMjJjZTAwNTgtZTJmNi00OTc3LWEwMjAtMTU3ZjYyNjM4MTJjIn0.jFEjzc09XvQm8mUrqxaSbRZWa0cvDnxiWy3alYwrHf0"

def make_http_request():
    """Synchronous HTTP request using urllib"""
    try:
        data = json.dumps({"data": {"notify": 1}}).encode('utf-8')
        req = urllib.request.Request(
            API_URL,
            data=data,
            headers={
                "Authorization": API_KEY,
                "Content-Type": "application/json"
            },
            method='PUT'
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            message = "Success!" if status_code == 200 else f"Error: {status_code}"
            return message
    except Exception as e:
        return f"Failed: {str(e)}"

async def send_notification_async():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, make_http_request)
    
    if result.startswith("Success"):
        messagebox.showinfo("Result", result)
    else:
        messagebox.showerror("Error", result)

def send_notification():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_notification_async())
    loop.close()

def main():
    root = tk.Tk()
    root.title("I-Remember Controller")
    root.geometry("250x120")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    
    tk.Label(root, text="I-Remember Controller", font=("Arial", 12, "bold")).pack(pady=10)
    tk.Button(root, text="Send Notification", command=send_notification, 
              font=("Arial", 11), bg="#4CAF50", fg="white", padx=15, pady=5).pack(pady=5)
    tk.Label(root, text="Click to set notify = 1", font=("Arial", 9), fg="gray").pack()
    
    root.mainloop()

if __name__ == "__main__":
    main()