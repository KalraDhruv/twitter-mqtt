# 🐦 twitter-mqtt

A simple, lightweight micro-blogging application—a "Twitter" clone—designed for **edge devices** and built entirely on the **MQTT (Message Queuing Telemetry Transport)** protocol for efficient, low-bandwidth communication.

***

## 🚀 Overview

This repository demonstrates a foundational publish/subscribe system where users can "tweet" messages using a Python script (the **Publisher**) and view them instantly on a web interface (the **Subscriber**). It is tailored for resource-constrained environments where traditional web infrastructure might be too heavy. 

***

## ✨ Key Features

* **MQTT-Based Messaging:** Leverages the **MQTT** protocol for asynchronous and reliable message delivery.
* **Edge Device Friendly:** Optimized for use in IoT and edge computing scenarios due to MQTT's minimal overhead.
* **Decoupled Architecture:** Separate components for publishing (`pub.py`) and subscribing (`sub.html`) allow for scalability and flexibility.
* **Simple Web Frontend:** A basic HTML/JavaScript client for viewing the feed in real-time.

***

## 💻 Technology Stack

* **Publisher:** **Python** (used to connect to the MQTT broker and send messages).
* **Subscriber Frontend:** **HTML**, **CSS**, and **JavaScript** (used to connect to the broker and display received messages).
* **Messaging Protocol:** **MQTT**.

***

## Working Demonstration

https://drive.google.com/file/d/1sgnZdqlfIkygvsuA9LB90eA7931SzxGn/view?usp=sharing
