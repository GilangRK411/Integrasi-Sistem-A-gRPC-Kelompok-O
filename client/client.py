import grpc
import chat_pb2
import chat_pb2_grpc
import time

class ChatClient:
    def __init__(self):
        # Inisialisasi koneksi ke server gRPC
        self.channel = grpc.insecure_channel('localhost:50059')
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
    
    def unary_chat(self, room, user, message):
        """Unary RPC: 1 request → 1 response"""
        start_time = time.time()
        request = chat_pb2.ChatMessage(
            room=room,
            user=user,
            message=message,
            timestamp=int(time.time())
        )
        response = self.stub.UnaryChat(request)
        latency = (time.time() - start_time) * 1000  # ms
        return response, latency
    
    def server_streaming_chat(self, room, user, message):
        """Server Streaming: 1 request → banyak response"""
        start_time = time.time()
        request = chat_pb2.ChatMessage(
            room=room,
            user=user,
            message=message,
            timestamp=int(time.time())
        )
        responses = self.stub.ServerStreamingChat(request)
        
        received_messages = []
        first_response_time = None
        for response in responses:
            if first_response_time is None:
                first_response_time = time.time()  # Waktu respons pertama
            received_messages.append(response)
        
        latency = (first_response_time - start_time) * 1000 if first_response_time else 0
        total_time = (time.time() - start_time) * 1000
        return received_messages, latency, total_time
    
    def client_streaming_chat(self, room, user, messages):
        """Client Streaming: Banyak request → 1 response"""
        start_time = time.time()
        
        def generate_messages():
            for msg in messages:
                yield chat_pb2.ChatMessage(
                    room=room,
                    user=user,
                    message=msg,
                    timestamp=int(time.time())
                )
        
        response = self.stub.ClientStreamingChat(generate_messages())
        latency = (time.time() - start_time) * 1000
        return response, latency
    
    def bidirectional_chat(self, room, user, messages):
        """Bidirectional Streaming: Banyak request ↔ banyak response"""
        start_time = time.time()
        
        def generate_messages():
            for msg in messages:
                yield chat_pb2.ChatMessage(
                    room=room,
                    user=user,
                    message=msg,
                    timestamp=int(time.time())
                )
        
        responses = self.stub.BidirectionalChat(generate_messages())
        
        received_messages = []
        first_response_time = None
        for response in responses:
            if first_response_time is None:
                first_response_time = time.time()
            received_messages.append(response)
        
        latency = (first_response_time - start_time) * 1000 if first_response_time else 0
        total_time = (time.time() - start_time) * 1000
        return received_messages, latency, total_time