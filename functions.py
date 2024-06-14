from PIL import Image
import io


def crop_image(img):
	image = Image.open(io.BytesIO(img))
	width, height = image.size
	if width == height:
	   return image
	offset  = int(abs(height-width)/2)
	if width>height:
		image = image.crop([offset,0,width-offset,height])
	else:
		image = image.crop([0,offset,width,height-offset])
	return image


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS