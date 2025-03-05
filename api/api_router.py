import json
from fastapi import APIRouter, HTTPException, WebSocket
from fastapi.encoders import jsonable_encoder
from cortex_service.conversation import ConversationService
from chat import Chat    
from cortex_service.models import Message
from utils.logger_config import service_logger as logger
api_router = APIRouter()

@api_router.websocket("/chat/stream")
async def stream_chat_api(websocket: WebSocket):
    try:
        await websocket.accept()
        
        # First receive user_id
        user_id = await websocket.receive_text()
        logger.info(f"WebSocket streaming connection established for user_id: {user_id}")
        
        # Then receive optional conversation_id (empty string if not provided)
        conversation_service = ConversationService()
        conversation_id = await websocket.receive_text()
        if conversation_id:
            logger.info(f"Continuing streaming conversation with id: {conversation_id}")
        else:
            logger.info(f"Starting new streaming conversation for user_id: {user_id}")
        
        # Then handle chat messages
        while True:
            data = await websocket.receive_text()
            message = Message(content=data, sender="user")
            conversation_id = conversation_service.store_message(message, user_id, conversation_id).id
            
            # Stream the response
            final_content = ""
            reasoning = []
            table = None
            logger.info(f"Streaming conversation with id: {conversation_id}")
            async for partial_result in Chat.stream_chat_payload(data, user_id, conversation_id):
                # Send each partial result as it becomes available
                await websocket.send_json({
                    "type": "stream",
                    "data": partial_result
                })
                
                # Keep track of the final content if it's a response
                if partial_result.get("type") == "query":
                    reasoning.append({"subquery": partial_result.get("content", "")})
                elif partial_result.get("type") == "response":
                    reasoning[-1]["response"] = partial_result.get("content", "")
                elif partial_result.get("type") == "complete":
                    final_content = partial_result.get("content", "")
                    if partial_result.get("table"):
                        table = json.loads(partial_result.get("table", ""))
            
            # Store the final message in the conversation
            if final_content:
                message_kwargs = {
                    "content": final_content,
                    "sender": "cortex"
                }
                if table:
                    message_kwargs["table"] = table
                    
                if reasoning:
                    message_kwargs["reasoning"] = reasoning
                
                final_message = Message(**message_kwargs)
                conversation_service.store_message(final_message, user_id, conversation_id)
            
            # Send a completion message
            await websocket.send_json({
                "type": "finished",
                "data": None
            })
                
    except Exception as e:
        logger.error("Error in /chat/stream websocket endpoint: %s", str(e))
        try:
            await websocket.send_json({
                "type": "error",
                "data": str(e)
            })
        except:
            pass
        raise HTTPException(status_code=500, detail="Internal Server Error")

@api_router.get("/get/conversation")
async def get_conversation_api(conversation_id: str):
    try:
        service = ConversationService()
        conversation = service.get_conversation(conversation_id=conversation_id)
        if conversation:
            return {"conversation": jsonable_encoder(conversation)}
        else:
            # Return a clear 404 if the conversation is not found
            raise HTTPException(
                status_code=404,
                detail=f"Conversation with id '{conversation_id}' not found"
            )
    except Exception as e:
        logger.error("Error in /get/conversation endpoint: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/get/conversation/all")
async def get_all_conversations_api(user_id: str):
    try:
        service = ConversationService()
        conversations = service.get_user_conversations(user_id)
        return {"conversations": conversations}
    except Exception as e:
        logger.error("Error in /get/conversation/all endpoint: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/conversation/{conversation_id}")
async def delete_conversation_api(conversation_id: str):
    try:
        logger.info(f"Deleting conversation with id: {conversation_id}")
        service = ConversationService()
        success = service.delete_conversation(conversation_id=conversation_id)
        if success:
            return {"message": f"Conversation '{conversation_id}' deleted successfully"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation with id '{conversation_id}' not found"
            )
    except Exception as e:
        logger.error("Error in /conversation/{conversation_id} DELETE endpoint: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))