
from core.memory import Memory
m = Memory()
m.client.delete_collection("facts")
m.client.delete_collection("history")
print("cleared")