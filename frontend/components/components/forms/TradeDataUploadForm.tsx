"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import SelectBox from "../commons/SelectBox";
import { Button } from "../ui/button";
import { Form, FormControl, FormField, FormItem, FormMessage } from "../ui/form";
import { Input } from "../ui/input";

interface UploadFormValues {
  file: FileList;
  brokerage_firm: string;
}

const brokerageFirms = [
  { label: "楽天証券", value: "rakuten" },
  // { label: "SBI証券", value: "sbi" },
  // { label: "マネックス証券", value: "monex" },
];

export default function TradeDataUploadForm() {
  const form = useForm<UploadFormValues>();
  const [uploading, setUploading] = useState(false);

  // Set default value for brokerage_firm
  form.setValue("brokerage_firm", brokerageFirms[0].value);

  async function onSubmit(data: UploadFormValues) {
    if (!data.file?.[0]) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", data.file[0]);
    formData.append("brokerage_firm", data.brokerage_firm);
    const res = await fetch("/api/analyses/upload", {
      method: "POST",
      body: formData,
    });
    setUploading(false);
    if (res.ok) {
      toast.success("アップロード成功", {
        description: "一覧をリロードします。",
        onDismiss: () => {
          location.reload();
        },
        onAutoClose: () => {
          location.reload();
        }
      });
    } else {
      toast.error("アップロードに失敗しました。");
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 w-full">
        <FormField
          control={form.control}
          name="brokerage_firm"
          rules={{ required: "証券会社を選択してください" }}
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <SelectBox
                  options={brokerageFirms}
                  value={field.value}
                  setValue={field.onChange}
                  placeholder="証券会社を選択"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="file"
          rules={{ required: "ファイルを選択してください" }}
          render={({ field }) => (
            <FormItem>
              <FormControl>
                <Input type="file" accept=".csv" onChange={e => field.onChange(e.target.files)} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={uploading} className="w-full">
          {uploading ? "アップロード中..." : "アップロード"}
        </Button>
      </form>
    </Form>
  );
}
