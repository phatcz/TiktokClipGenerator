# Story Object v0.1

Story = Object กลางที่ทุก module จะใช้ร่วมกัน

## Input
- goal
- product
- audience
- platform

## Output
- scenes[] (เรียงตามเวลา)

## Scene Structure
- id
- purpose (hook / conflict / reveal / close)
- emotion
- duration (seconds)
- description (text)
{
  "goal": "ขายคอร์สออนไลน์",
  "product": "AI Creator Tool",
  "audience": "มือใหม่ ไม่เก่งเทค",
  "platform": "Facebook Reel",
  "scenes": [
    {
      "id": 1,
      "purpose": "hook",
      "emotion": "curious",
      "duration": 3,
      "description": "ตั้งคำถามว่าทำไมคนส่วนใหญ่ใช้ AI ไม่เป็น"
    },
    {
      "id": 2,
      "purpose": "conflict",
      "emotion": "frustrated",
      "duration": 5,
      "description": "โชว์ความยุ่งยากของ prompt และ tool"
    },
    {
      "id": 3,
      "purpose": "reveal",
      "emotion": "relief",
      "duration": 5,
      "description": "แนะนำเครื่องมือที่ทำให้ AI ง่าย"
    },
    {
      "id": 4,
      "purpose": "close",
      "emotion": "confident",
      "duration": 4,
      "description": "เชิญชวนให้สมัครใช้งาน"
    }
  ]
}
