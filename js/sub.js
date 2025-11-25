let mqtt;
let subscriptions = [];
let messageCount = 0;
const host = 'localhost';
const port = 9001;

// Connect to MQTT broker
function connectMQTT() {
    mqtt = new Paho.MQTT.Client(
	host, 
	Number(port), 
	"/mqtt",
	"mqtt_client_" + parseInt(Math.random() * 10000, 10)
    );
    
    mqtt.onConnectionLost = onConnectionLost;
    mqtt.onMessageArrived = onMessageArrived;
    
    mqtt.connect({
	timeout: 3,
	useSSL: false,
	cleanSession: true,
	onSuccess: onConnect,
	onFailure: function(message) {
	    console.error("Connection failed:", message);
	    $('#status').html('<strong>●</strong> Connection failed: ' + message.errorMessage)
		.removeClass().addClass('status-box alert alert-danger');
	    $('#connStatus').text('Disconnected').removeClass().addClass('badge badge-danger');
	}
    });
}

function onConnect() {
    console.log("Connected successfully!");
    $('#status').html('<strong>●</strong> Connected to MQTT broker at ' + host + ':' + port)
	.removeClass().addClass('status-box alert alert-success');
    $('#connStatus').text('Connected').removeClass().addClass('badge badge-success');
}

function onConnectionLost(response) {
    console.error("Connection lost:", response.errorMessage);
    $('#status').html('<strong>●</strong> Connection lost. Reconnecting...')
	.removeClass().addClass('status-box alert alert-warning');
    $('#connStatus').text('Reconnecting').removeClass().addClass('badge badge-warning');
    setTimeout(connectMQTT, 3000);
}

function onMessageArrived(message) {
    const topic = message.destinationName;
    const payload = message.payloadString;
    const timestamp = new Date().toLocaleTimeString();
    
    console.log("Message received:", topic, payload);
    
    // Update statistics
    messageCount++;
    $('#messageCount').text(messageCount + ' messages');
    $('#msgCount').text(messageCount);
    $('#lastTopic').text(topic);
    
    // Add message to feed
    addMessageToFeed(topic, payload, timestamp);
}

function subscribeToTopic() {
    const topic = $('#newTopic').val().trim();
    
    if (!topic) {
	alert('Please enter a topic!');
	return;
    }
    
    if (subscriptions.includes(topic)) {
	alert('Already subscribed to this topic!');
	return;
    }
    
    try {
	mqtt.subscribe(topic, { qos: 0 });
	subscriptions.push(topic);
	updateSubscriptionList();
	$('#newTopic').val('');
	$('#subCount').text(subscriptions.length);
	console.log("Subscribed to:", topic);
    } catch (error) {
	console.error("Subscription error:", error);
	alert('Failed to subscribe: ' + error.message);
    }
}

function unsubscribeFromTopic(topic) {
    try {
	mqtt.unsubscribe(topic);
	subscriptions = subscriptions.filter(t => t !== topic);
	updateSubscriptionList();
	$('#subCount').text(subscriptions.length);
	console.log("Unsubscribed from:", topic);
    } catch (error) {
	console.error("Unsubscribe error:", error);
    }
}

function quickSubscribe(topic) {
    $('#newTopic').val(topic);
    subscribeToTopic();
}

function updateSubscriptionList() {
    const listDiv = $('#subscriptionList');
    
    if (subscriptions.length === 0) {
	listDiv.html(`
	    <div class="empty-state">
		<div class="empty-state-icon">📭</div>
		<p>No active subscriptions</p>
	    </div>
	`);
	return;
    }
    
    let html = '';
    subscriptions.forEach(topic => {
	html += `
	    <div class="subscription-item">
		<span>📌 ${topic}</span>
		<button class="btn-unsubscribe" onclick="unsubscribeFromTopic('${topic}')">
		    ✕ Unsubscribe
		</button>
	    </div>
	`;
    });
    
    listDiv.html(html);
}

function addMessageToFeed(topic, payload, timestamp) {
    const listDiv = $('#messageList');
    
    // Remove empty state if present
    if (messageCount === 1) {
	listDiv.html('');
    }
    
    const messageHtml = `
	<div class="message-item">
	    <div class="message-topic">${topic}</div>
	    <div class="message-payload">${payload}</div>
	    <div class="message-time">⏰ ${timestamp}</div>
	</div>
    `;
    
    listDiv.prepend(messageHtml);
    
    // Keep only last 50 messages
    const messages = listDiv.find('.message-item');
    if (messages.length > 50) {
	messages.last().remove();
    }
}

function clearMessages() {
    messageCount = 0;
    $('#messageList').html(`
	<div class="empty-state">
	    <div class="empty-state-icon">💬</div>
	    <p>No messages received yet</p>
	    <small>Subscribe to topics to start receiving messages</small>
	</div>
    `);
    $('#messageCount').text('0 messages');
    $('#msgCount').text('0');
}

// Initialize on page load
$(document).ready(function() {
    connectMQTT();
});
