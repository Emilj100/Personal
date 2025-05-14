Baseline Model

To begin, I implemented a simple convolutional neural network with two convolutional layers (32 and 64 filters, respectively, each with a 3×3 kernel), each followed by 2×2 max pooling. After flattening, I added a single dense layer of 128 neurons and a final softmax output for 43 classes. I trained for 10 epochs using the Adam optimizer and categorical crossentropy loss, normalizing pixel values to the 0–1 range. This baseline achieved around 88% validation accuracy, but I noticed the training accuracy was substantially higher, indicating overfitting.

Adding Regularization

To combat overfitting, I introduced a 50% dropout layer after the dense layer. This modest change increased validation accuracy to 91% and narrowed the gap between training and validation metrics. I also experimented with moving dropout into the convolutional blocks (using a 25% rate immediately after pooling), which helped slightly but made training slower.

Testing Depth and Capacity

Next, I added a third convolutional block (128 filters) before flattening, hoping to capture more complex features. While training accuracy rose quickly, validation accuracy plateaued around 92%, and the model began to overfit more. Reducing the number of neurons in the dense layer (from 128 to 64) helped marginally but at the cost of overall performance.

Data Augmentation

To further improve generalization, I incorporated simple augmentation—random rotations (±15°), shifts (±10%), and zoom (±10%). This step increased robustness noticeably: validation accuracy climbed to 94% and training curves looked smoother. The augmented model handled skewed or slightly blurred images better, mirroring real-world variations.

Final Observations

Normalization (dividing pixel values by 255) was critical: without it, training was unstable and slow.

Dropout after the dense layer provided the biggest boost against overfitting; dropout in convolutional layers had diminishing returns for this dataset.

Data augmentation delivered the most consistent improvement in validation metrics.

Overall, combining a three-block CNN with dropout and data augmentation yielded the best balance of accuracy and generalization.