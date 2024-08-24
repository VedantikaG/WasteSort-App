import os

import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt


def get_full_path(path):
    return os.path.join(os.getcwd(), path)


def process_image(file_path: str, write_annotations: bool = False):
    # Load the SavedModel
    model_path = get_full_path(
        os.path.join(
            "AI Module",
            "saved_model"
        )
    )
    model = tf.saved_model.load(model_path)

    file_name = os.path.basename(file_path)
    # Load an input image (replace 'path/to/your/image.jpg' with the actual path)
    input_image = cv2.imread(get_full_path(file_path))
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)  # Convert to RGB format

    # Preprocess the input image (adjust according to your model's requirements)
    preprocessed_image = tf.image.resize(
        input_image, (512, 512)
    )  # Replace height and width with your model's input size
    preprocessed_image = tf.image.convert_image_dtype(
        preprocessed_image, dtype=tf.uint8
    )  # Convert to uint8
    preprocessed_image = np.expand_dims(
        preprocessed_image, axis=0
    )  # Add batch dimension

    # Attempt to use the default signature
    try:
        infer = model.signatures[tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY]
    except KeyError:
        raise ValueError(
            "The SavedModel does not have a default signature. Please specify the correct signature key."
        )

    # Run inference
    predictions = infer(tf.constant(preprocessed_image))

    # Post-process predictions (adjust according to your model's output format)
    boxes = predictions["detection_boxes"].numpy()
    scores = predictions["detection_scores"].numpy()
    classes = predictions["detection_classes"].numpy()

    # Visualize results
    for i in range(boxes.shape[1]):
        box = boxes[0, i]
        score = scores[0, i]
        class_id = int(classes[0, i])

        # Filter out low-confidence detections (adjust threshold as needed)
        if score > 0.5:
            ymin, xmin, ymax, xmax = box
            xmin = int(xmin * input_image.shape[1])
            xmax = int(xmax * input_image.shape[1])
            ymin = int(ymin * input_image.shape[0])
            ymax = int(ymax * input_image.shape[0])

            # Draw bounding box on the image
            cv2.rectangle(input_image, (xmin, ymin), (xmax, ymax), (255, 0, 0), 2)
            class_label = f"Class {class_id} ({score:.2f})"
            cv2.putText(
                input_image,
                class_label,
                (xmin, ymin - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2,
            )

    # Display the annotated image
    # plt.imshow(input_image)
    # plt.show()

    return cv2.imencode('.jpg', cv2.cvtColor(input_image, cv2.COLOR_RGB2BGR))[1].tobytes()


if __name__ == "__main__":
    process_image("../AI Module/input/litter-trash-garbage-overflow.jpg", True)
