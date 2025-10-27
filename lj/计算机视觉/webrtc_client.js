// This script assumes it's running in a browser environment with WebRTC support.
// Functions like 'sendOfferToRemote' and 'sendCandidateToRemote' are placeholders
// and would typically involve a signaling server (e.g., using WebSockets) to exchange
// SDP offers/answers and ICE candidates with the other peer.

// Placeholder for sending signaling messages to the other peer.
function sendOfferToRemote(offer) {
    console.log("Sending offer to remote peer:", offer);
    // In a real application, this would send the offer through a signaling server.
}

function sendCandidateToRemote(candidate) {
    console.log("Sending ICE candidate to remote peer:", candidate);
    // In a real application, this would send the candidate through a signaling server.
}

// Configuration for the RTCPeerConnection (e.g., STUN/TURN servers)
const configuration = {
    'iceServers': [{
        'urls': 'stun:stun.l.google.com:19302' // Public STUN server
    }]
};

let pc; // RTCPeerConnection
let dc; // RTCDataChannel

// 1. Get user's local media (audio in this case)
navigator.mediaDevices.getUserMedia({ video: false, audio: true })
    .then(function (stream) {
        console.log("Successfully obtained media stream.");

        // 2. Create a new RTCPeerConnection
        pc = new RTCPeerConnection(configuration);
        console.log("RTCPeerConnection created.");

        // 3. Add local audio tracks to the connection
        stream.getTracks().forEach(function (track) {
            pc.addTrack(track, stream);
        });
        console.log("Local audio tracks added to the connection.");

        // 4. Handle ICE candidates
        pc.onicecandidate = function (event) {
            if (event.candidate) {
                // Send the candidate to the other peer via the signaling server
                sendCandidateToRemote(event.candidate);
            }
        };

        // 5. Handle incoming remote tracks
        pc.ontrack = function (event) {
            console.log("Received remote track.");
            var audio = new Audio();
            audio.srcObject = event.streams[0];
            audio.play();
        };

        // --- Data Channel Setup (for text chat) ---

        // 6a. Create a data channel (for the initiating peer)
        dc = pc.createDataChannel('chat', { ordered: true });
        console.log("Data channel 'chat' created.");

        // 6b. Or handle an incoming data channel (for the receiving peer)
        pc.ondatachannel = function (event) {
            console.log("Received remote data channel.");
            dc = event.channel;
            setupDataChannelEvents(dc);
        };

        setupDataChannelEvents(dc);

        // 7. Create and send an offer to the other peer
        return pc.createOffer();
    })
    .then(function (offer) {
        console.log("Offer created.");
        return pc.setLocalDescription(offer);
    })
    .then(function () {
        // Send the offer to the other peer via the signaling server
        sendOfferToRemote(pc.localDescription);
    })
    .catch(function (error) {
        console.error('Could not get media stream or create PeerConnection:', error);
    });

/**
 * Sets up the event listeners for a data channel.
 * @param {RTCDataChannel} channel The data channel to set up.
 */
function setupDataChannelEvents(channel) {
    channel.onmessage = function (event) {
        console.log('Received message:', event.data);
    };

    channel.onopen = function () {
        console.log('Data channel opened');
        // When the channel is open, we can send messages
        if (channel.readyState === "open") {
            channel.send('Hello, world!');
        }
    };

    channel.onclose = function () {
        console.log('Data channel closed');