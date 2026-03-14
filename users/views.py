from django.shortcuts import render, redirect
from .models import RegisteredUser
from django.core.files.storage import FileSystemStorage
import nltk
import os
nltk.data.path.append(r"C:\Users\DELL\AppData\Roaming\nltk_data")

def register_view(request):
    msg = ''
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        image = request.FILES.get('image')

        # Basic validation
        if not (name and email and mobile and password and image):
            msg = "All fields are required."
        else:
            # Save image manually
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            img_url = fs.url(filename)

            # Save user with is_active=False
            RegisteredUser.objects.create(
                name=name,
                email=email,
                mobile=mobile,
                password=password,
                image=filename,
                is_active=False
            )
            msg = "Registered successfully! Wait for admin approval."

    return render(request, 'register.html', {'msg': msg})

from django.utils import timezone

from django.utils import timezone
import pytz

def user_login(request):
    msg = ''
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        try:
            user = RegisteredUser.objects.get(name=name, password=password)
            if user.is_active:
                # Convert current time to IST
                ist = pytz.timezone('Asia/Kolkata')
                local_time = timezone.now().astimezone(ist)

                # Save user info in session
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                request.session['user_image'] = user.image.url  # image URL
                request.session['login_time'] = local_time.strftime('%I:%M:%S %p')

                return redirect('user_homepage')
            else:
                msg = "Your account is not activated yet."
        except RegisteredUser.DoesNotExist:
            msg = "Invalid credentials."

    return render(request, 'user_login.html', {'msg': msg})

def admin_login(request):
    msg = ''
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        if name == 'admin' and password == 'admin':
            return redirect('admin_home')
        else:
            msg = "Invalid admin credentials."

    return render(request, 'admin_login.html', {'msg': msg})

def admin_home(request):
    return render(request, 'admin_home.html')
    
def admin_dashboard(request):
    users = RegisteredUser.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})

def activate_user(request, user_id):
    user = RegisteredUser.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('admin_dashboard')

def deactivate_user(request, user_id):
    user = RegisteredUser.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect('admin_dashboard')

def delete_user(request, user_id):
    user = RegisteredUser.objects.get(id=user_id)
    user.delete()
    return redirect('admin_dashboard')



def home(request):
    return render(request, 'home.html')

def user_homepage(request):
    if 'user_id' not in request.session:
        # User not logged in, redirect to login page
        return redirect('user_login')

    user_name = request.session.get('user_name')
    user_image = request.session.get('user_image')
    login_time = request.session.get('login_time')

    context = {
        'user_name': user_name,
        'user_image': user_image,
        'login_time': login_time,
    }
    return render(request, 'users/user_homepage.html', context)

def user_logout(request):
    request.session.flush()  # Clears all session data
    return redirect('user_login')



import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import RegisteredUser

otp_storage = {}  # Temporary dictionary to store OTPs

def send_otp(email):
    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    otp_storage[email] = otp

    subject = "Password Reset OTP"
    message = f"Your OTP for password reset is: {otp}"
    from_email = "saikumardatapoint1@gmail.com"  # Change this to your email
    send_mail(subject, message, from_email, [email])

    return otp

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if RegisteredUser.objects.filter(email=email).exists():
            send_otp(email)
            request.session["reset_email"] = email  # Store email in session
            return redirect("verify_otp")
        else:
            messages.error(request, "Email not registered!")

    return render(request, "forgot_password.html")

def verify_otp(request):
    if request.method == "POST":
        otp_entered = request.POST.get("otp")
        email = request.session.get("reset_email")

        if otp_storage.get(email) and str(otp_storage[email]) == otp_entered:
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid OTP!")

    return render(request, "verify_otp.html")

def reset_password(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        email = request.session.get("reset_email")

        if RegisteredUser.objects.filter(email=email).exists():
            user = RegisteredUser.objects.get(email=email)
            user.password = new_password  # Updating password
            user.save()
            messages.success(request, "Password reset successful! Please log in.")
            return redirect("user_login")

    return render(request, "reset_password.html")


def project_overview(request):
    return render(request, 'users/overview.html')



## AI code

import os
import fitz  # PyMuPDF
import json
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
#import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt

# === Your Gemini 1.5 Flash API Key ===
#GOOGLE_API_KEY = "AIzaSyD_OQErfN8ISovhF1oS0pRj_7rDs73lm3s"

# Configure Gemini
#genai.configure(api_key=GOOGLE_API_KEY)
#model = genai.GenerativeModel('models/gemini-1.5-flash')

# === Extract text from uploaded PDF ===
import fitz
import re

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    # ---------- VERY IMPORTANT CLEANING ----------
    # remove line breaks
    text = text.replace("\n", " ")

    # remove multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # add sentence stops if missing
    text = re.sub(r'([a-z])([A-Z])', r'\1. \2', text)

    # ensure minimum punctuation
    if "." not in text:
        text = text.replace(" ", ". ")

    return text

# === Generate MCQs using Gemini 1.5 Flash ===
# def generate_mcqs(text, subject, level, num):
#     prompt = f"""
# Generate {num} multiple-choice questions (MCQs) based on the following text. Each question should be relevant to the subject "{subject}" and have a difficulty level of "{level}". Provide the response in JSON format as a list of dictionaries, each containing:
# - "question": The question text.
# - "options": A list of four options.
# - "answer": The correct option.

# # Text:
# # {text}
# # """
#     #response = model.generate_content(prompt)
#     try:
#         # Clean and parse the response text
#         response_text = response.text.strip()
#         # Remove any code block markers if present
#         if response_text.startswith("```json"):
#             response_text = response_text[7:]
#         if response_text.endswith("```"):
#             response_text = response_text[:-3]
#         mcqs = json.loads(response_text)
#         return mcqs
#     except Exception as e:
#         print("Error parsing JSON:", e)
#         return []

# === Upload Form and PDF Processing ===
@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST':
        pdf_file = request.FILES['pdf_file']
        subject = request.POST['subject']
        level = request.POST['level']
        num_mcqs = int(request.POST['num_mcqs'])

        file_path = default_storage.save(f"temp/{pdf_file.name}", pdf_file)
        full_path = os.path.join(default_storage.location, file_path)
        text = extract_text_from_pdf(full_path)
        text = text.replace("\n", " ")
        text = text[:10000]
        mcqs = generate_mcqs(text, subject, level, num_mcqs)
        # convert to JSON before saving
        request.session['mcqs'] = json.dumps(mcqs)
        request.session.modified = True
        return redirect('quiz')
    return render(request, 'users/upload.html')

# === Display the Quiz ===
def quiz(request):
    mcqs_json = request.session.get('mcqs', '[]')
    mcqs = json.loads(mcqs_json)
    return render(request, 'users/quiz.html', {'mcqs': mcqs})

@csrf_exempt

def result(request):
    mcqs_json = request.session.get('mcqs', '[]')
    mcqs = json.loads(mcqs_json)
    user_answers = {}
    score = 0

    results = []

    for i, q in enumerate(mcqs):
        user_answer = request.POST.get(f'question_{i}')
        correct_answer = q['answer']
        is_correct = user_answer == correct_answer
        if is_correct:
            score += 1
        results.append({
            'question': q['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })

    return render(request, 'users/result.html', {
        'score': score,
        'total': len(mcqs),
        'results': results
    })
import nltk
import random
import spacy

nlp = spacy.load("en_core_web_sm")

import re


nlp = spacy.load("en_core_web_sm")

def generate_mcqs(text, subject, level, num_mcqs):

    sentences = re.split(r'[.!?]', text)

    mcqs = []

    for sent in sentences:

        # clean sentence
        sent = sent.strip()
        if len(sent) < 40:
            continue

        doc = nlp(sent)

        # take important words (nouns + proper nouns + adjectives)
        keywords = [token.text for token in doc 
                    if token.pos_ in ["NOUN", "PROPN", "ADJ"] 
                    and token.is_stop == False
                    and token.is_alpha == True]

        if len(keywords) < 3:
            continue

        answer = random.choice(keywords)

        # create blank question
        question = re.sub(r'\b' + re.escape(answer) + r'\b', "__________", sent, count=1)

        # generate options
        options = [answer]

        while len(options) < 4:
            word = random.choice(keywords)
            if word not in options and len(word) > 2:
                options.append(word)

        random.shuffle(options)

        mcqs.append({
            "question": question,
            "options": options,
            "answer": answer
        })

        if len(mcqs) >= num_mcqs:
            break
        # fallback if no mcqs generated
        if len(mcqs) == 0:
            words = text.split()
            for i in range(min(num_mcqs, 5)):
                answer = words[random.randint(20, len(words)-20)]
                question = f"What is the meaning of '{answer}' in the given text?"
                
                options = random.sample(words, 3)
                options.append(answer)
                random.shuffle(options)

                mcqs.append({
                    "question": question,
                    "options": options,
                    "answer": answer
                    })

    return mcqs