"use client"

import { Button } from "@/components/ui/button"
import { PopoverContent } from "@/components/ui/popover"
import { APP_NAME } from "@/lib/config"
import { isSupabaseEnabled } from "@/lib/supabase/config"
import Image from "next/image"
import Link from "next/link"

export function PopoverContentAuth() {
  if (!isSupabaseEnabled) {
    return null
  }
  return (
    <PopoverContent
      className="w-[300px] overflow-hidden rounded-xl p-0"
      side="top"
      align="start"
    >
      <Image
        src="/og-image.png"
        alt={`calm paint generate by ${APP_NAME}`}
        width={300}
        height={128}
        className="h-32 w-full object-cover"
      />
      <div className="p-3">
        <p className="text-primary mb-1 text-base font-medium">
          Login to try more features for free
        </p>
        <p className="text-muted-foreground mb-5 text-base">
          Create Projects, invite team members, and more.
        </p>
        <Button asChild variant="secondary" className="w-full text-base" size="lg">
          <Link href="/auth">Open sign-in page</Link>
        </Button>
        <p className="text-muted-foreground mt-3 text-sm">
          Use email and password or request a magic link from the sign-in page.
        </p>
      </div>
    </PopoverContent>
  )
}
