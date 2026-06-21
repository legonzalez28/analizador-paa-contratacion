require('dotenv').config()
const OpenAI = require('openai')

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
})

async function main() {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
  { role: "user", content: "Explícame qué es una API como si tuviera 10 años" }
]
  })

  console.log(response.choices[0].message.content)
}

main()