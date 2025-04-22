import grpc
from concurrent import futures
import time
import chat_pb2
import chat_pb2_grpc
from collections import defaultdict

class ChatServicer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.rooms = defaultdict(list)
    
    def UnaryChat(self, request, context):
        # Simpan pesan
        self.rooms[request.room].append(request)
        
        # Buat respons
        response = chat_pb2.ChatMessage(
            room=request.room,
            user="Server",
            message=f"Received your message in {request.room} room",
            timestamp=int(time.time())
        )
        return response
    
    def ServerStreamingChat(self, request, context):
        # Kirim balasan segera
        yield chat_pb2.ChatMessage(
            room=request.room,
            user="Server",
            message=f"Welcome to server streaming in {request.room} room",
            timestamp=int(time.time())
        )
        
        # Simpan pesan awal
        self.rooms[request.room].append(request)
        
        # Kirim update periodik
        for i in range(1, 6):
            time.sleep(1)
            yield chat_pb2.ChatMessage(
                room=request.room,
                user="Server",
                message=f"Server update {i}/5",
                timestamp=int(time.time())
            )
    
    def ClientStreamingChat(self, request_iterator, context):
        message_count = 0
        last_message = None
        
        for request in request_iterator:
            message_count += 1
            last_message = request
            self.rooms[request.room].append(request)
        
        return chat_pb2.ChatMessage(
            room=last_message.room if last_message else "unknown",
            user="Server",
            message=f"Received {message_count} messages",
            timestamp=int(time.time())
        )
    
    def BidirectionalChat(self, request_iterator, context):
        for request in request_iterator:
            # Simpan pesan
            self.rooms[request.room].append(request)
            
            # Kirim balasan
            yield chat_pb2.ChatMessage(
                room=request.room,
                user="Server",
                message=f"Echo: {request.message}",
                timestamp=int(time.time())
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServicer(), server)
    server.add_insecure_port('[::]:50059')
    server.start()
    print("Server started on port 50059")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()