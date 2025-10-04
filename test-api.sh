#!/usr/bin/env bash

# WebSec Chat Platform - API Testing Script (Linux/macOS)
# This script demonstrates all available API endpoints

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# API Base URL
API_URL="https://localhost:8443/api/v1"
COOKIE_FILE="cookies.txt"

# Clean up old cookies
rm -f $COOKIE_FILE

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  WebSec Chat Platform API Demo${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Test 1: Register Users
echo -e "${YELLOW}[1/11] Registering users...${NC}"
echo -e "${GREEN}POST /register${NC}"

ALICE_DATA=$(curl -k -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "profile_name": "Alice Wonderland",
    "password": "SecurePass123!"
  }')
echo "Alice registered:"
echo "$ALICE_DATA" | jq '.'
ALICE_ID=$(echo "$ALICE_DATA" | jq -r '.id')
echo ""

BOB_DATA=$(curl -k -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob",
    "profile_name": "Bob Builder",
    "password": "SecurePass123!"
  }')
echo "Bob registered:"
echo "$BOB_DATA" | jq '.'
BOB_ID=$(echo "$BOB_DATA" | jq -r '.id')
echo ""

CHARLIE_DATA=$(curl -k -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "charlie",
    "profile_name": "Charlie Chaplin",
    "password": "SecurePass123!"
  }')
echo "Charlie registered:"
echo "$CHARLIE_DATA" | jq '.'
CHARLIE_ID=$(echo "$CHARLIE_DATA" | jq -r '.id')
echo ""

read -p "Press Enter to continue..."

# Test 2: Login
echo -e "${YELLOW}[2/11] Logging in as Alice...${NC}"
echo -e "${GREEN}POST /login${NC}"

curl -k -s -X POST "$API_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "SecurePass123!"
  }' \
  -c $COOKIE_FILE | jq '.'
echo ""

read -p "Press Enter to continue..."

# Test 3: Get Current User
echo -e "${YELLOW}[3/11] Getting current user info...${NC}"
echo -e "${GREEN}GET /me${NC}"

curl -k -s "$API_URL/me" -b $COOKIE_FILE | jq '.'
echo ""

read -p "Press Enter to continue..."

# Test 4: Search Users
echo -e "${YELLOW}[4/11] Searching for users...${NC}"
echo -e "${GREEN}GET /users/search?q=alice${NC}"

curl -k -s "$API_URL/users/search?q=alice" -b $COOKIE_FILE | jq '.'
echo ""

echo -e "${GREEN}GET /users/search?q=bob&limit=5${NC}"
curl -k -s "$API_URL/users/search?q=bob&limit=5" -b $COOKIE_FILE | jq '.'
echo ""

read -p "Press Enter to continue..."

# Test 5: Send Messages
echo -e "${YELLOW}[5/11] Sending messages from Alice to Bob...${NC}"
echo -e "${GREEN}POST /messages${NC}"

curl -k -s -X POST "$API_URL/messages" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d "{
    \"recipient_id\": \"$BOB_ID\",
    \"content\": \"Hey Bob, how are you doing?\"
  }" | jq '.'
echo ""

curl -k -s -X POST "$API_URL/messages" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d "{
    \"recipient_id\": \"$BOB_ID\",
    \"content\": \"Looking forward to chatting with you!\"
  }" | jq '.'
echo ""

curl -k -s -X POST "$API_URL/messages" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d "{
    \"recipient_id\": \"$CHARLIE_ID\",
    \"content\": \"Hi Charlie! Welcome to the platform.\"
  }" | jq '.'
echo ""

read -p "Press Enter to continue..."

# Test 6: Login as Bob and Reply
echo -e "${YELLOW}[6/11] Logging in as Bob and replying...${NC}"
echo -e "${GREEN}POST /login (as Bob)${NC}"

curl -k -s -X POST "$API_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob",
    "password": "SecurePass123!"
  }' \
  -c $COOKIE_FILE | jq '.'
echo ""

echo -e "${GREEN}POST /messages (Bob -> Alice)${NC}"
curl -k -s -X POST "$API_URL/messages" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d "{
    \"recipient_id\": \"$ALICE_ID\",
    \"content\": \"Hi Alice! I'm doing great, thanks for asking!\"
  }" | jq '.'
echo ""

curl -k -s -X POST "$API_URL/messages" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d "{
    \"recipient_id\": \"$ALICE_ID\",
    \"content\": \"How about you?\"
  }" | jq '.'
echo ""

read -p "Press Enter to continue..."

# Test 7: Get Conversations List
echo -e "${YELLOW}[7/11] Getting Bob's conversations list...${NC}"
echo -e "${GREEN}GET /messages/conversations${NC}"

curl -k -s "$API_URL/messages/conversations" -b $COOKIE_FILE | jq '.'
echo ""

read -p "Press Enter to continue..."

# Test 8: Get Conversation Messages
echo -e "${YELLOW}[8/11] Getting full conversation between Bob and Alice...${NC}"
echo -e "${GREEN}GET /messages/$ALICE_ID${NC}"

curl -k -s "$API_URL/messages/$ALICE_ID" -b $COOKIE_FILE | jq '.'
echo ""

read -p "Press Enter to continue..."

# Test 9: Login back as Alice
echo -e "${YELLOW}[9/11] Logging back in as Alice...${NC}"
echo -e "${GREEN}POST /login (as Alice)${NC}"

curl -k -s -X POST "$API_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "SecurePass123!"
  }' \
  -c $COOKIE_FILE | jq '.'
echo ""

# Test 10: Get Alice's Conversations
echo -e "${YELLOW}[10/11] Getting Alice's conversations list...${NC}"
echo -e "${GREEN}GET /messages/conversations${NC}"

curl -k -s "$API_URL/messages/conversations" -b $COOKIE_FILE | jq '.'
echo ""

read -p "Press Enter to continue..."

# Test 11: Logout
echo -e "${YELLOW}[11/11] Logging out...${NC}"
echo -e "${GREEN}POST /logout${NC}"

curl -k -s -X POST "$API_URL/logout" -b $COOKIE_FILE | jq '.'
echo ""

# Clean up
rm -f $COOKIE_FILE

echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}  All API endpoints tested! ✓${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}Summary of tested endpoints:${NC}"
echo "  ✓ POST   /register"
echo "  ✓ POST   /login"
echo "  ✓ GET    /me"
echo "  ✓ GET    /users/search"
echo "  ✓ POST   /messages"
echo "  ✓ GET    /messages/conversations"
echo "  ✓ GET    /messages/{user_id}"
echo "  ✓ POST   /logout"
echo ""
echo -e "${CYAN}User IDs created:${NC}"
echo "  Alice:   $ALICE_ID"
echo "  Bob:     $BOB_ID"
echo "  Charlie: $CHARLIE_ID"
echo ""
echo -e "${YELLOW}Tip: View interactive docs at https://localhost:8443/api/v1/docs${NC}"
