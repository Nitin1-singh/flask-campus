-- AlterTable
ALTER TABLE "User" ADD COLUMN     "username" TEXT;

-- CreateTable
CREATE TABLE "Quiz" (
    "id" SERIAL NOT NULL,
    "quizName" TEXT,
    "question" TEXT[],

    CONSTRAINT "Quiz_pkey" PRIMARY KEY ("id")
);
