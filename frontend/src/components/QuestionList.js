import Question from './Question'
import React from 'react'
export const QuestionList = ({questions, categories, questionAction})=>{
  return (
    <>
      <h2>Questions</h2>
      {questions.map((q) => (
      <Question
        key={q.id}
        question={q.question}
        answer={q.answer}
        category={categories[q.category]} 
        difficulty={q.difficulty}
        questionAction={questionAction(q.id)}
      />
    ))}
    </>
    )
}