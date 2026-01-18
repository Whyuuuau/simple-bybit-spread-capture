#!/bin/bash
# Infinite loop to keep bot running inside Docker/Linux

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

while true
do
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}🚀 STARTING BYBIT BOT - $(date)${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    # Run the bot
    python main.py
    
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}⚠️ BOT STOPPED/CRASHED - $(date)${NC}"
    echo -e "${RED}♻️ Restarting in 5 seconds...${NC}"
    echo -e "${RED}Press Ctrl+C to stop permanently${NC}"
    echo -e "${RED}========================================${NC}"
    
    sleep 5
done
