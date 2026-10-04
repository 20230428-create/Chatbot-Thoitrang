@echo off
title Fashion AI Stylist Launcher
echo ============================================================
echo   KHOI DONG FASHION AI STYLIST CHATBOT (PORTABLE)
echo ============================================================
if exist "%~dp0FashionAI_Chatbot_Portable.exe" (
    start "" "%~dp0FashionAI_Chatbot_Portable.exe"
) else (
    start "" "%~dp0dist\FashionAI_Chatbot_Portable.exe"
)
exit
