import openai

prompt = "Translate the following English text to Korean:\n\n\"Hello, how are you today?"

completion = openai.ChatCompletion.create(
    model="gpt-4o-mini",  # 번역만이라면 4o-mini도 충분
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

korean = completion.choices[0].message.content.strip()
print("번역 :", korean)

