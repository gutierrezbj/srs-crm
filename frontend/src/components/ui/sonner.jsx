import { Toaster as Sonner } from "sonner"

const Toaster = ({
  ...props
}) => {
  return (
    <Sonner
      theme="dark"
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-slate-800 group-[.toaster]:text-slate-100 group-[.toaster]:border-slate-700 group-[.toaster]:shadow-lg",
          description: "group-[.toast]:text-slate-400",
          actionButton:
            "group-[.toast]:bg-cyan-400 group-[.toast]:text-slate-900",
          cancelButton:
            "group-[.toast]:bg-slate-700 group-[.toast]:text-slate-300",
        },
      }}
      {...props} />
  );
}

export { Toaster }
