using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using System.Drawing;

namespace csClient_UI
{
    public partial class Form1 : Form
    {
        private Socket clientSocket;
        private Thread receiveThread;
        private TextBox ipv6TextBox;
        private TextBox usernameTextBox;
        private TextBox receivedMessagesTextBox;
        private TextBox messageTextBox;
        private Button connectButton;
        private Button sendMessageButton;
        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            base.OnFormClosing(e);

            if (clientSocket != null && clientSocket.Connected)
            {
                clientSocket.Shutdown(SocketShutdown.Both);
                clientSocket.Close();
            }

            if (receiveThread != null && receiveThread.IsAlive)
            {
                receiveThread.Abort();
            }
        }

        public Form1()
        {
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            // Initialize the UI elements
            ipv6TextBox = new TextBox();
            usernameTextBox = new TextBox();
            receivedMessagesTextBox = new TextBox();
            messageTextBox = new TextBox();
            connectButton = new Button();
            sendMessageButton = new Button();

            ipv6TextBox.Location = new Point(10, 10);
            ipv6TextBox.Size = new Size(300, 20);

            usernameTextBox.Location = new Point(10, 40);
            usernameTextBox.Size = new Size(300, 20);

            receivedMessagesTextBox.Location = new Point(10, 70);
            receivedMessagesTextBox.Size = new Size(400, 300);
            receivedMessagesTextBox.Multiline = true;
            receivedMessagesTextBox.ReadOnly = true;

            messageTextBox.Location = new Point(10, 380);
            messageTextBox.Size = new Size(300, 20);

            connectButton.Location = new Point(320, 10);
            connectButton.Size = new Size(100, 30);
            connectButton.Text = "Connect";
            connectButton.Click += connectButton_Click;

            sendMessageButton.Location = new Point(320, 380);
            sendMessageButton.Size = new Size(100, 30);
            sendMessageButton.Text = "Send message";
            sendMessageButton.Click += sendMessageButton_Click;

            Controls.Add(ipv6TextBox);
            Controls.Add(usernameTextBox);
            Controls.Add(receivedMessagesTextBox);
            Controls.Add(messageTextBox);
            Controls.Add(connectButton);
            Controls.Add(sendMessageButton);

            // Set the default form size
            Size = new Size(450, 450);
        }

        private void connectButton_Click(object sender, EventArgs e)
        {
            if (clientSocket != null && clientSocket.Connected)
            {
                MessageBox.Show("You are already connected to the server.");
                return;
            }

            string ipAddress = ipv6TextBox.Text;

            int port = 10000;
            clientSocket = new Socket(AddressFamily.InterNetworkV6, SocketType.Stream, ProtocolType.Tcp);

            try
            {
                clientSocket.Connect(ipAddress, port);
            }
            catch (SocketException ex)
            {
                MessageBox.Show($"Failed to connect: {ex.Message}");
                return;
            }

            // Change the color of the Connect button to green
            connectButton.BackColor = Color.Green;

            // Send the user's username to the server
            string username = usernameTextBox.Text;
            byte[] usernameBytes = Encoding.UTF8.GetBytes(username);
            clientSocket.Send(usernameBytes);

            // Start the receive thread
            receiveThread = new Thread(() =>
            {
                while (true)
                {
                    byte[] buffer = new byte[1024];
                    int numBytes = clientSocket.Receive(buffer);
                    string message = Encoding.UTF8.GetString(buffer, 0, numBytes);
                    Invoke(new Action(() =>
                    {
                        receivedMessagesTextBox.AppendText(message + Environment.NewLine);
                    }));
                }
            });
            receiveThread.Start();
        }

        private void sendMessageButton_Click(object sender, EventArgs e)
        {
            // Send a message to the server
            string message = messageTextBox.Text;
            byte[] messageBytes = Encoding.UTF8.GetBytes(message);
            clientSocket.Send(messageBytes);
        }
    }
}
