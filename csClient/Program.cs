using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

class Program
{
    static void Main(string[] args)
    {
        Console.Write("Enter server IPv6 address: ");
        string host = Console.ReadLine();
        int port = 55555;

        // Create a socket object
        Socket clientSocket = new Socket(AddressFamily.InterNetworkV6, SocketType.Stream, ProtocolType.Tcp);

        // Connect to the server
        clientSocket.Connect(host, port);

        // Get the client username
        Console.Write("Enter a username: ");
        string username = Console.ReadLine();
        byte[] usernameBytes = Encoding.UTF8.GetBytes(username);
        clientSocket.Send(usernameBytes);

        Thread receiveThread = new Thread(() =>
        {
            // Receives messages from the server and prints them to the console
            while (true)
            {
                byte[] buffer = new byte[1024];
                int numBytes = clientSocket.Receive(buffer);
                string message = Encoding.UTF8.GetString(buffer, 0, numBytes);
                Console.WriteLine(message);
            }
        });

        receiveThread.Start();

        while (true)
        {
            // Get user input and send it to the server
            string message = Console.ReadLine();
            byte[] messageBytes = Encoding.UTF8.GetBytes(message);
            clientSocket.Send(messageBytes);
        }
    }
}