v2.1  
使用了wenglor IDK，只使用了最简单的三个函数connect disconnect 和获取数据。  
两个文件中，pseudo main是可以用的，另一个wenglor to kafka是模仿原有代码写的，可能不太好用


v2.2.3
测试通过了使用mqtt向wenglor——to——kafka发送命令
测试通过了使用docker
    一点小问题是，docker里没有办法实时地显示pseudoMain和consumer里输出的数据，但是不影响主文件的使用



##资料
###3D模块  
potree  
镜像： https://hub.docker.com/r/jonazpiazu/potree  
`docker run -dit --name=potree_viewer --rm -p 8080:80 -v "$PWD":/shared  potree`  
使用http://localhost:8080/  

Potree 是一个基于 JavaScript 的点云可视化库，它可以在客户端动态加载点云数据。因此，如果你的点云数据是逐步从 Kafka 中读取的，并且你能够将这些数据转换为 Potree 支持的格式（如 LAS、LAZ、PLY 等），那么 Potree 是可以实现动态加载的。  

要实现动态加载点云数据，你需要在 Potree 中编写逻辑来处理新数据的到达。一种常见的方法是在客户端使用 WebSocket 或者其他实时通信技术，监听 Kafka 中新数据的到达，并在接收到新数据时，动态加载它们到 Potree 中。  

以下是一个简单的流程，演示如何实现动态加载点云数据：  

    **从 Kafka 中读取数据：**使用 Kafka 相关的库或者工具，编写一个消费者应用，用于从 Kafka 中消费新的点云数据。  

    **转换数据格式：**在消费者应用中，将从 Kafka 中读取的数据转换为 Potree 支持的格式（如 LAS、LAZ、PLY 等）。你可以使用相应的库或者工具来进行数据转换。  

    **实时通信：**在客户端应用中，使用 WebSocket 或者其他实时通信技术，与服务器建立连接，并监听新数据的到达。  

    **动态加载数据：**当接收到新数据时，使用 Potree 的 API 在客户端动态加载新的点云数据。你可以通过调用 Potree 的相应函数来加载新的点云数据，并更新可视化效果。  

通过以上流程，你可以实现从 Kafka 中动态加载点云数据，并实时更新 Potree 中的可视化效果。需要注意的是，动态加载大量数据可能会带来性能方面的挑战，因此需要合理设计和优化你的应用。  