#!/bin/bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/accounts/register/ -H 'Content-Type: application/json' -d '{"phone":"254711999999","password":"password123","first_name":"Jane","last_name":"Doe","role":"farmer"}' | jq -r .token)
if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/accounts/login/ -H 'Content-Type: application/json' -d '{"username":"254711999999","password":"password123"}' | jq -r .token)
fi
echo "Token: $TOKEN"
curl -v -s -X POST http://localhost:8000/api/v1/pricing/quote/ -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" -d '{"crop":"MAIZE","acreage":2.5,"h3_index":"8928308280fffff"}'
