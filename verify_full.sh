#!/bin/bash

BASE_URL="http://127.0.0.1:8000/school-api"
EMAIL="full_test_$(date +%s)@example.com"
PASSWORD="Password1!#"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}===== STARTING FULL VERIFICATION =====${NC}"

# 1. Registration
echo -e "\n${GREEN}[1/8] Registration${NC}"
curl -s -X POST "$BASE_URL/registr" \
     -H "Content-Type: application/json" \
     -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" | jq

# 2. Authorization
echo -e "\n${GREEN}[2/8] Authorization${NC}"
RESPONSE=$(curl -s -X POST "$BASE_URL/auth" \
     -H "Content-Type: application/json" \
     -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")
echo $RESPONSE | jq
TOKEN=$(echo $RESPONSE | jq -r '.token')

if [ "$TOKEN" == "null" ]; then
    echo -e "${RED}Failed to get token${NC}"
    exit 1
fi
echo "Token: $TOKEN"

# 3. List Courses & Select Course
echo -e "\n${GREEN}[3/8] List Courses & Select Course${NC}"
COURSES_RES=$(curl -s -X GET "$BASE_URL/courses/" -H "Authorization: Bearer $TOKEN")
echo $COURSES_RES | jq
# Select course with name "Future Course 2027"
COURSE_ID=$(echo $COURSES_RES | jq -r '.data[] | select(.name == "Future Course 2027") | .id')

if [ -z "$COURSE_ID" ] || [ "$COURSE_ID" == "null" ]; then
    echo -e "${RED}Course 'Future Course 2027' not found. Running setup script...${NC}"
    ./venv/bin/python setup_test_data.py
    # Refetch
    COURSES_RES=$(curl -s -X GET "$BASE_URL/courses/" -H "Authorization: Bearer $TOKEN")
    COURSE_ID=$(echo $COURSES_RES | jq -r '.data[] | select(.name == "Future Course 2027") | .id')
fi
echo "Selected Course ID: $COURSE_ID"

# 4. Buy Course (Enrollment)
echo -e "\n${GREEN}[4/8] Buy Course (Create Order)${NC}"
BUY_RES=$(curl -s -X POST "$BASE_URL/courses/$COURSE_ID/buy/" \
     -H "Authorization: Bearer $TOKEN")
echo $BUY_RES | jq
PAY_URL=$(echo $BUY_RES | jq -r '.pay_url')
ORDER_ID=$(echo $PAY_URL | sed 's/.*order_id=//')
echo "Extracted Order ID: $ORDER_ID"

# 5. Check Orders (Pending) & Get Enrollment ID
echo -e "\n${GREEN}[5/8] Check Orders (Pending)${NC}"
ORDERS_RES=$(curl -s -X GET "$BASE_URL/orders" -H "Authorization: Bearer $TOKEN")
echo $ORDERS_RES | jq
ENROLLMENT_ID=$(echo $ORDERS_RES | jq -r ".data[] | select(.course.id == $COURSE_ID) | .id")
echo "Enrollment ID: $ENROLLMENT_ID"

# 6. Webhook (Payment Success)
echo -e "\n${GREEN}[6/8] Payment Webhook (Success)${NC}"
WEBHOOK_RES=$(curl -s -X POST "$BASE_URL/payment-webhook" \
     -H "Content-Type: application/json" \
     -d "{\"order_id\": \"$ORDER_ID\", \"status\": \"success\"}")
# Webhook returns 204 (Empty)
echo "Status Code: $(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/payment-webhook" -H "Content-Type: application/json" -d "{\"order_id\": \"$ORDER_ID\", \"status\": \"success\"}")"

# 7. Check Orders (Success) & Cancel Attempt
echo -e "\n${GREEN}[7/8] Check Status & Try Cancel Paid${NC}"
# Re-fetch orders to see success status
curl -s -X GET "$BASE_URL/orders" -H "Authorization: Bearer $TOKEN" | jq

echo "Attempting to cancel paid enrollment ID: $ENROLLMENT_ID"
CANCEL_RES=$(curl -s -X GET "$BASE_URL/orders/$ENROLLMENT_ID" \
     -H "Authorization: Bearer $TOKEN")
echo $CANCEL_RES | jq

# 8. Check Certificate
echo -e "\n${GREEN}[8/8] Check Certificate${NC}"
# Logic: ends with 1 -> success
CERT_RES_GOOD=$(curl -s -X POST "$BASE_URL/check-sertificate" \
     -H "Content-Type: application/json" \
     -d "{\"sertikate_number\": \"123451\"}")
echo "Check '123451' (Expect Success):"
echo $CERT_RES_GOOD | jq

CERT_RES_BAD=$(curl -s -X POST "$BASE_URL/check-sertificate" \
     -H "Content-Type: application/json" \
     -d "{\"sertikate_number\": \"123452\"}")
echo "Check '123452' (Expect Failed):"
echo $CERT_RES_BAD | jq

echo -e "\n${GREEN}===== VERIFICATION COMPLETE =====${NC}"
