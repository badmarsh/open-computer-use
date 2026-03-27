"use client"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { isSupabaseEnabled } from "@/lib/supabase/config"
import Link from "next/link"

type DialogCollaborativeAuthProps = {
  open: boolean
  setOpen: (open: boolean) => void
}

export function DialogCollaborativeAuth({ open, setOpen }: DialogCollaborativeAuthProps) {
  if (!isSupabaseEnabled) {
    return null
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-xl">
            Sign in to Create Projects
          </DialogTitle>
          <DialogDescription className="pt-2 text-base">
            Create projects to build your product with AI. Sign in with email or magic link to get started.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="mt-6 sm:justify-center">
          <Button asChild className="w-full text-base" size="lg">
            <Link href="/auth">Open sign-in page</Link>
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
