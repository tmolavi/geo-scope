# InTen Client Panel Integration Blueprint: AI Visibility Evidence Audit

**Document Identifier:** `INTEN-INT-AIVIS-2026.1`  
**Host Repository:** `/Users/taghimolavi/aether-nexus-site`  
**App Framework:** React 18 + Vite + TanStack Router (`routeTree.gen.ts`)  
**Proposed Route File:** `src/routes/tools.ai-visibility-audit.tsx` (Route Path: `/tools/ai-visibility-audit` or `/client/tools/ai-visibility-audit`)  
**Status:** Feature Flagged (`FEATURE_AI_VISIBILITY_AUDIT=false`), Read-Only MVP, No Production Deployment  

---

## 1. Codebase Discovery & Architectural Mapping

Following Phase 1 inspection of the InTen application repository at `/Users/taghimolavi/aether-nexus-site`, the architectural building blocks were verified:

| Subsystem | Existing InTen Architecture | AI Visibility Integration Hook |
| :--- | :--- | :--- |
| **Router** | TanStack Router (`@tanstack/react-router`) with file-based routing | Create `src/routes/tools.ai-visibility-audit.tsx` (matches existing `tools.geo-audit.tsx` pattern). |
| **Auth & Session** | `src/admin/auth.tsx` (`useAdminAuth`, JWT bearer tokens) | Gate paid historical and competitor views behind active user session. |
| **RBAC Permissions**| `src/admin/permissions.tsx` (`can(user, 'view_analytics')`) | Restrict scheduled real-provider runs to authorized admin/analyst roles. |
| **Tenancy & Plans** | `src/admin/types.ts` (`SubscriptionPlan`: `free`, `starter`, `pro`) | Free tier gets single-domain heuristic scan; paid tiers unlock multi-provider empirical benchmarks. |
| **UI Components** | Radix UI primitives (`@/components/ui/`), Tailwind CSS, Lucide icons | Native reuse of `Button`, `Input`, `Card`, `Badge`, `Tabs`, and Sonner toast. |
| **Design Language** | InTen Brand System (`@/components/inten/Header`, `Footer`) | Persian RTL layout, cyan/blue gradient accents, dark mode compatibility. |

---

## 2. Proposed Route Specification

### 2.1 Route Definition (`src/routes/tools.ai-visibility-audit.tsx`)

```tsx
import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Sparkles, ShieldCheck, Search, Globe, AlertTriangle, Database } from "lucide-react";
import { Header } from "@/components/inten/Header";
import { Footer } from "@/components/inten/Footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

// Feature Flag Guard
const FEATURE_AI_VISIBILITY_AUDIT_ENABLED = 
  import.meta.env.VITE_FEATURE_AI_VISIBILITY_AUDIT === "true" || false;

export const Route = createFileRoute("/tools/ai-visibility-audit")({
  head: () => ({
    meta: [
      { title: "ممیزی مبتنی بر شواهد حضور در هوش مصنوعی — اینتن" },
      { name: "description", content: "سنجش علمی و مستند سهم حضور برند در ChatGPT، Gemini و Perplexity بدون داده‌های ساختگی." },
    ],
  }),
  component: AiVisibilityAuditTool,
});

function AiVisibilityAuditTool() {
  const [domain, setDomain] = useState("");
  const [locale, setLocale] = useState("fa-IR");
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditResult, setAuditResult] = useState<any>(null);

  if (!FEATURE_AI_VISIBILITY_AUDIT_ENABLED) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex flex-col justify-center items-center p-6 text-center">
        <AlertTriangle className="w-12 h-12 text-amber-400 mb-4" />
        <h1 className="text-2xl font-bold mb-2">این ابزار در فاز آزمایشی داخلی است</h1>
        <p className="text-slate-400 max-w-md">قابلیت AI Visibility Evidence Audit به‌زودی برای مشتریان فعال خواهد شد.</p>
      </div>
    );
  }

  // Implementation follows the PRD: Read-only heuristic scan with unmeasured empirical status
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Header />
      <main className="max-w-6xl mx-auto px-4 py-16">
        {/* Hero & Audit Form */}
        <div className="text-center mb-12">
          <Badge variant="outline" className="text-cyan-400 border-cyan-400/30 mb-4">
            Evidence-First GEO Audit
          </Badge>
          <h1 className="text-4xl font-extrabold tracking-tight mb-4">
            ممیزی شفاف و مستند دیده‌شدن برند در هوش مصنوعی
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto">
            ارزیابی آمادگی فنی (L1–L4) و شواهد تجربی حضور برند (L5) بدون امتیازهای صوری و بدون حدس و گمان.
          </p>
        </div>

        {/* Domain Input Form */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-2xl mx-auto mb-12">
          <div className="flex flex-col sm:flex-row gap-3">
            <Input
              type="text"
              placeholder="example.com"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="bg-slate-950 border-slate-700 text-white"
            />
            <Button className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold px-6">
              شروع ممیزی رایگان
            </Button>
          </div>
        </div>

        {/* Foundational Disclaimer Card */}
        <div className="bg-slate-900/50 border border-slate-800/80 rounded-xl p-6 text-sm text-slate-300">
          <div className="flex items-center gap-2 font-semibold text-cyan-400 mb-2">
            <ShieldCheck className="w-5 h-5" />
            اصل بنیادین اندازه‌گیری در اینتن:
          </div>
          <p className="font-mono text-xs text-slate-400 mb-2">
            Mention ≠ Citation ≠ Recommendation ≠ Position ≠ Share of Model
          </p>
          <p>
            گزارش رایگان شامل بررسی ساختار فنی، داده‌های ساختاریافته و ابهام‌زدایی نام تجاری است. 
            وضعیت اندازه‌گیری عینی در مدل‌های آنلاین تا زمان اجرای پرس‌وجوهای زنده با برچسب <strong>UNMEASURED</strong> نمایش داده می‌شود.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}
```

---

## 3. Security, Tenancy & Deployment Controls

1. **Feature Flag Isolation:** Initial release is hidden behind `VITE_FEATURE_AI_VISIBILITY_AUDIT="false"`. Can be enabled for internal QA without affecting public traffic.
2. **Zero Paid API Execution:** The initial component operates strictly in read-only / heuristic mode. No automated charges or rate-limited external calls.
3. **No Automatic Database Migrations:** Uses existing Supabase / TanStack Query caches without mutating existing client billing records.
