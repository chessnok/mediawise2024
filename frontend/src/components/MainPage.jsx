import React, { useState, useRef } from "react";
import axios from 'axios';
import '../MainPage.css';
import Config from "../config";
let robot = require('../assets/robot.jpg');
let document = require('../assets/document.png');
let ApiUrl = Config.API_URL;

const MainPage = () => {
    const [messages, setMessages] = useState([
        { author: 1, time: "2:33 am", text: "User question" },
        { author: 0, time: "2:44 am", text: "Robot response" },
        { author: 1, time: "3:15 am", text: "Another user question" },
        { author: 0, time: "3:16 am", text: "Another robot response" }
    ]);

    const [chats, setChats] = useState([
        { name: "Chat 1", chat_id: "12345" },
        { name: "Chat 2", chat_id: "67890" },
        { name: "Chat 3", chat_id: "54321" }
    ]);

    const [warning, setWarning] = useState("");
    const [chatWarning, setChatWarning] = useState("");
    const messageInputRef = useRef(null);
    const chatInputRef = useRef(null);

    const handleNewMessage = async () => {
        const text = messageInputRef.current.value;
        const userId = "placeholder_user_id";
        const chatId = "placeholder_chat_id";

        if (text.length < 10) {
            setWarning("Сообщение слишком короткое");
            return;
        }

        const lastMessage = messages[messages.length - 1];
        if (lastMessage && lastMessage.author === 1) {
            setWarning("Ожидаем ответ бота на предыдущий вопрос");
            return;
        }

        setWarning("");
        const newMessage = { author: 1, time: new Date().toLocaleTimeString(), text };
        setMessages(prevMessages => [...prevMessages, newMessage]);

        try {
            await axios.post(`${ApiUrl}/apply`, {
                user_id: userId,
                chat_id: chatId,
                text: text
            });
            messageInputRef.current.value = "";
        } catch (error) {
            console.error("Ошибка при отправке сообщения:", error);
        }
    };

    const handleCreateChat = () => {
        const chatName = chatInputRef.current.value.trim();
        if (chatName === "") {
            setChatWarning("Название чата не может быть пустым");
            return;
        }
        if (chats.some(chat => chat.name === chatName)) {
            setChatWarning("Чат с таким названием уже существует");
            return;
        }

        setChatWarning("");
        const newChat = {
            name: chatName,
            chat_id: Math.floor(Math.random() * 100000).toString()
        };

        setChats(prevChats => [...prevChats, newChat]);
        chatInputRef.current.value = ""; // Очистка поля ввода после добавления
    };

    return (
        <main className="content">
            <div className="container p-0">
                <h1 className="h3 mb-3">Messages</h1>
                <div className="card">
                    <div className="row g-0">
                        <div className="col-12 col-lg-5 col-xl-3 border-right">
                            <div className="px-4 d-none d-md-block">
                                <div className="d-flex align-items-center">
                                    <div className="flex-grow-1">
                                        <input
                                            type="text"
                                            className="form-control my-3"
                                            placeholder="Введите название чата"
                                            ref={chatInputRef} // Реф для поля ввода чата
                                        />
                                    </div>
                                    <button
                                        className="btn btn-primary ml-2"
                                        onClick={handleCreateChat}
                                    >
                                        Создать
                                    </button>
                                </div>
                                {chatWarning && (
                                    <div className="text-danger mt-2">
                                        {chatWarning}
                                    </div>
                                )}
                            </div>
                            {chats.map((chat, index) => (
                                <a
                                    key={index}
                                    href="#"
                                    className="list-group-item list-group-item-action border-0"
                                >
                                    <div className="d-flex align-items-start">
                                        <img
                                            src={document}
                                            className="rounded-circle mr-1"
                                            alt={chat.name}
                                            width={40}
                                            height={40}
                                        />
                                        <div className="flex-grow-1 ml-3">
                                            {chat.name}
                                            <div className="small">
                                                <span className="text-muted">ID: {chat.chat_id}</span>
                                            </div>
                                        </div>
                                    </div>
                                </a>
                            ))}
                            <hr className="d-block d-lg-none mt-1 mb-0"/>
                        </div>
                        <div className="col-12 col-lg-7 col-xl-9">
                            <div className="py-2 px-4 border-bottom d-none d-lg-block">
                                {/* Заголовок чата */}
                            </div>
                            <div className="position-relative">
                                <div className="chat-messages p-4">
                                    {messages.map((message, index) => (
                                        <div
                                            key={index}
                                            className={`chat-message-${message.author === 1 ? 'right' : 'left'} pb-4`}
                                        >
                                            <div>
                                                <img
                                                    src={message.author === 1
                                                        ? "https://bootdey.com/img/Content/avatar/avatar1.png"
                                                        : robot
                                                    }
                                                    className="rounded-circle mr-1"
                                                    alt={message.author === 1 ? "You" : "Robot"}
                                                    width={40}
                                                    height={40}
                                                />
                                                <div className="text-muted small text-nowrap mt-2">
                                                    {message.time}
                                                </div>
                                            </div>
                                            <div className={`flex-shrink-1 bg-light rounded py-2 px-3 ${message.author === 1 ? 'mr-3' : 'ml-3'}`}>
                                                <div className="font-weight-bold mb-1">
                                                    <b>{message.author === 1 ? "You" : "Robot"}</b>
                                                </div>
                                                {message.text}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                {warning && (
                                    <div className="text-danger px-4 py-2">
                                        {warning}
                                    </div>
                                )}
                            </div>
                            <div className="flex-grow-0 py-3 px-4 border-top">
                                <div className="input-group">
                                    <input
                                        type="text"
                                        className="form-control"
                                        placeholder="Type your message"
                                        ref={messageInputRef} // Реф для поля ввода сообщения
                                    />
                                    <button
                                        className="btn btn-primary"
                                        onClick={handleNewMessage}
                                    >
                                        Send
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
};

export default MainPage;
