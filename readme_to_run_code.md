Steps to reproduce the experiment using the code:

1. Download the KMNIST dataset from the GitHub page in the numpy format: [KMNIST Dataset](https://github.com/rois-codh/kmnist/tree/master?tab=readme-ov-file). It consists of four files, two for training and two for testing. Each pair of files contains images and labels.

2. Install the required libraries: 
   - numpy
   - torch
   - torchvision
   - skorch
   - modAL
   - seaborn
   - matplotlib
   - scikit-learn
   - wandb (wandb will also require registration to the service before running the code)

3. After registering with wandb, follow these instructions to properly log in and track your experiments: [Wandb Quickstart](https://docs.wandb.ai/quickstart#:~:text=Sign%20up%20for%20a%20free,Python%203%20environment%20using%20pip%20).

4. When loading the datasets in the code, use np.load() and specify the path where you saved the downloaded dataset.

5. If the experiment is run on a non-Apple chip, set the device to “coda” instead of “mps”. Replace the line of code in the dedicated cell under “set device to gpu”.

6. Choose the query strategy in the “Active Learning Loop” section among the three alternatives proposed. Adjust model.train() and model.eval() as instructed in the code comments, in the for loop below.

7. For non-MC dropout strategies, remove the “sample_per_forward_pass” and “num_cycles” parameters, as they are only required by the BALD MC dropout strategy.

8. Adjust the wandb initialization with the name of your project and configuration details.

9. Run the code.
