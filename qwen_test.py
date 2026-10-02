import ollama
import time
from PIL import Image
MODEL = "qwen2.5vl:7b"
VERIFY_PROMPT = (
    'Carefully examine this image for any of the following: '
    'exposed cleavage or midriff, underwear/lingerie/sheer nightwear, '
    'an upskirt angle, a sexualized pose, a swimsuit or beach scene, '
    'characters kissing or in intimate embrace, clothing that is tight '
    'or fitted in a way that shows the bust, waist, hips, or legs, '
    'or a camera angle emphasizing the chest or buttocks even a little. '
    'or anything you think might be considered not safe to watch around religious people, even if not inappropriate for other cultures for kids or anyone in general in moderate or religious/islamic households. '
    'answer with YES or NO '
)

test_list0 = [
    'frames/frame_0041.jpg', 'frames/frame_0068.jpg', 'frames/frame_0084.jpg',
    'frames/frame_0100.jpg', 'frames/frame_0181.jpg', 'frames/frame_0183.jpg',
    'frames/frame_0190.jpg', 'frames/frame_0192.jpg', 'frames/frame_0211.jpg',
    'frames/frame_0238.jpg', 'frames/frame_0255.jpg', 'frames/frame_0342.jpg',
    'frames/frame_0377.jpg', 'frames/frame_0379.jpg', 'frames/frame_0383.jpg',
    'frames/frame_0385.jpg', 'frames/frame_0415.jpg', 'frames/frame_0421.jpg',
    'frames/frame_0428.jpg', 'frames/frame_0459.jpg', 'frames/frame_0518.jpg',
    'frames/frame_0521.jpg', 'frames/frame_0526.jpg', 'frames/frame_0527.jpg',
    'frames/frame_0532.jpg', 'frames/frame_0556.jpg', 'frames/frame_0577.jpg',
    'frames/frame_0586.jpg', 'frames/frame_0689.jpg', 'frames/frame_0755.jpg',
    'frames/frame_0776.jpg', 'frames/frame_0831.jpg', 'frames/frame_0843.jpg',
    'frames/frame_0844.jpg', 'frames/frame_0848.jpg', 'frames/frame_0866.jpg',
    'frames/frame_0896.jpg', 'frames/frame_0906.jpg', 'frames/frame_0911.jpg',
    'frames/frame_0922.jpg', 'frames/frame_0930.jpg', 'frames/frame_0931.jpg',
    'frames/frame_0933.jpg', 'frames/frame_0956.jpg'
]


test_list1 = ['frames/frame_0100.jpg', 'frames/frame_0181.jpg', 'frames/frame_0183.jpg',
    'frames/frame_0190.jpg', 'frames/frame_0192.jpg', 'frames/frame_0211.jpg'

]



for frame in test_list1:
    start = time.time()
    response = ollama.chat(
        model=MODEL,
        messages=[{
            'role': 'user',
            'content': VERIFY_PROMPT,
            'images': [frame],
        }],
        options={'num_predict': 100}
    )
    elapsed = time.time() - start
    print(f"{frame}: {response['message']['content']} ({elapsed:.1f}s)")