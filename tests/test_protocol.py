import requests
import pytest
import asyncio
from websocket import create_connection
import websocket
import json
from jsonrpcclient import parse_json, request_json


@pytest.mark.asyncio
async def test_create_visualization(server):
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:1234/ws")
    ws.send("create_visualization")
    response = await ws.recv()
    print("response", response)
    assert True
