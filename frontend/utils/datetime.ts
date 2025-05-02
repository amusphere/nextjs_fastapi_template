import { format } from "date-fns";

export const dateFormat = (datetime: number | string | Date, formatStr: string = "yyyy-MM-dd") => {
  let date = datetime;
  if (typeof datetime === "number") {
    date = new Date(datetime * 1000);
  }
  if (typeof datetime === "string") {
    date = new Date(datetime);
  }
  return format(date, formatStr);
}
