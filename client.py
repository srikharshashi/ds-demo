import requests

def upload_image(api_url, image_path):
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(api_url, files=files,headers={"username":"shashi"})
    return response

# Replace 'your_api_url' with your actual API URL
# Replace 'your_image_path' with the path to the image you want to upload
response = upload_image('http://localhost:2000/upload-image', '2517915.jpg')

# Print the response from the server
print(response.text)
