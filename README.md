<!--
   Copyright 2026 UCP Authors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
-->

# Universal Commerce Protocol (UCP) Samples

This directory contains sample implementations and client scripts for the
Universal Commerce Protocol (UCP).

## Featured Applications

### Enhanced Business Agent with AP2 Payment (NEW!)

A production-ready AI-powered shopping assistant with UCP product discovery and **complete AP2 payment protocol implementation**.

*   **Application**: [Documentation](enhanced-app/README.md)
    *   Located in `enhanced-app/`.
    *   **Features**:
        *   🤖 AI Chat Interface with Ollama integration (Qwen/Gemma models)
        *   🏪 Merchant Portal for product and pricing management
        *   💳 **Complete AP2 Payment Protocol** ✅
            *   🔐 WebAuthn Passkey authentication (FIDO2)
            *   💾 Encrypted payment card storage (Fernet encryption, consumer side only)
            *   🔒 Token-based payment (merchant never sees raw card numbers)
            *   📝 Payment mandate creation and passkey signing
            *   ✅ OTP challenge for high-risk transactions (10-30% probability)
            *   🎯 Complete payment flow: Registration → Cart → Checkout → Passkey Auth → Payment Receipt
            *   🛡️ Fixed test card: 5123 1212 2232 5678 (Mastercard)
        *   💾 Persistent SQLite databases (separate for products and credentials)
        *   🎨 Beautiful modern UI with React and Tailwind CSS
        *   🔧 RESTful API with FastAPI
        *   📦 Dual Protocol: UCP for commerce + AP2 for payment
    *   **Architecture**:
        *   **Chat Backend (8452)** - UCP Client + Credentials Provider (stores user credentials, cards, passkeys)
        *   **Merchant Backend (8453)** - UCP Server (products) + AP2 Merchant Agent (payment processor with Ollama)
        *   **Separation of Concerns**: User credentials never touch merchant backend
    *   **Ports**:
        *   Port 8450 → Chat Interface (maps to https://chat.abhinava.xyz)
        *   Port 8451 → Merchant Portal (maps to https://app.abhinava.xyz)
        *   Port 8452 → Chat Backend API (credentials provider + AP2 consumer agent)
        *   Port 8453 → Merchant Backend API (UCP server + AP2 merchant agent)
    *   **Quick Start**: `cd enhanced-app && ./start-split.sh`
    *   **Stop Services**: `cd enhanced-app && ./stop-split.sh`
    *   **Status**: ✅ **FULLY IMPLEMENTED** - UCP product discovery, AI chat, cart management, user registration with passkey, payment card storage, AP2 payment flow with OTP challenge, checkout UI

## Sample Implementations

### Python

A reference implementation of a UCP Merchant Server using Python and FastAPI.

*   **Server**: [Documentation](rest/python/server/README.md)

    *   Located in `rest/python/server/`.
    *   Demonstrates capability discovery, checkout session management, payment
        processing, and order lifecycle.
    *   Includes simulation endpoints for testing.

*   **Client**:
    [Happy Path Script](rest/python/client/flower_shop/simple_happy_path_client.py)

    *   Located in `rest/python/client/`.
    *   A script demonstrating a full "happy path" user journey (discovery ->
        checkout -> payment).

### Node.js

A reference implementation of a UCP Merchant Server using Node.js, Hono, and
Zod.

*   **Server**: [Documentation](rest/nodejs/README.md)
    *   Located in `rest/nodejs/`.
    *   Demonstrates implementation of UCP specifications for shopping,
        checkout, and order management using a Node.js stack.

## Getting Started

Please refer to the specific README files linked above for detailed instructions
on how to set up, run, and test each sample.
