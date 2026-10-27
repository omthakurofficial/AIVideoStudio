Every time a developer pushes code, a CI pipeline wakes up. It builds a Docker image, runs the automated tests, and pushes the image to a container registry.

Next, Kubernetes pulls that image and schedules it onto worker nodes in a cluster. If a container crashes, Kubernetes notices and starts a replacement automatically.

A load balancer then spreads incoming user requests across the healthy containers, so users never see the failure.
