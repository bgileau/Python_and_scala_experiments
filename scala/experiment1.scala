// Databricks notebook source

import org.apache.spark.sql.functions.desc
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import spark.implicits._
import org.apache.spark.sql.expressions.Window

// COMMAND ----------


spark.conf.set("spark.sql.legacy.timeParserPolicy","LEGACY")

// COMMAND ----------


val customSchema = StructType(Array(StructField("lpep_pickup_datetime", StringType, true), StructField("lpep_dropoff_datetime", StringType, true), StructField("PULocationID", IntegerType, true), StructField("DOLocationID", IntegerType, true), StructField("passenger_count", IntegerType, true), StructField("trip_distance", FloatType, true), StructField("fare_amount", FloatType, true), StructField("payment_type", IntegerType, true)))

// COMMAND ----------


val df = spark.read
   .format("com.databricks.spark.csv")
   .option("header", "true") // Use first line of all files as header
   .option("nullValue", "null")
   .schema(customSchema)
   .load("/FileStore/tables/nyc_tripdata.csv") // the csv file which you want to work with
   .withColumn("pickup_datetime", from_unixtime(unix_timestamp(col("lpep_pickup_datetime"), "MM/dd/yyyy HH:mm")))
   .withColumn("dropoff_datetime", from_unixtime(unix_timestamp(col("lpep_dropoff_datetime"), "MM/dd/yyyy HH:mm")))
   .drop($"lpep_pickup_datetime")
   .drop($"lpep_dropoff_datetime")

// COMMAND ----------

// LOAD THE "taxi_zone_lookup.csv" FILE SIMILARLY AS ABOVE. CAST ANY COLUMN TO APPROPRIATE DATA TYPE IF NECESSARY.


val customSchema_zone = StructType(Array(StructField("LocationID", IntegerType, true), StructField("Borough", StringType, true), StructField("Zone", StringType, true), StructField("service_zone", StringType, true)))

val df_zone = spark.read
   .format("com.databricks.spark.csv")
   .option("header", "true") // Use first line of all files as header
   .option("nullValue", "null")
   .schema(customSchema_zone)
   .load("/FileStore/tables/taxi_zone_lookup.csv") // the csv file which you want to work with

// COMMAND ----------


// Some commands that you can use to see your dataframes and results of the operations. You can comment the df.show(5) and uncomment display(df) to see the data differently. You will find these two functions useful in reporting your results.
// display(df)
df.show(5) // view the first 5 rows of the dataframe

// COMMAND ----------


// Filter the data to only keep the rows where "PULocationID" and the "DOLocationID" are different and the "trip_distance" is strictly greater than 2.0 (>2.0).

// VERY VERY IMPORTANT: ALL THE SUBSEQUENT OPERATIONS MUST BE PERFORMED ON THIS FILTERED DATA

val df_filter = df.filter($"PULocationID" =!= $"DOLocationID" && $"trip_distance" > 2.0)
df_filter.show(5)

// COMMAND ----------

// PART 1a: The top-5 most popular drop locations - "DOLocationID", sorted in descending order - if there is a tie, then one with lower "DOLocationID" gets listed first
// Output Schema: DOLocationID int, number_of_dropoffs int 

val df_1a = df_filter.select("DOLocationID")
  .groupBy("DOLocationID")
  .agg(count("DOLocationID").alias("number_of_dropoffs"))
  .orderBy(desc("number_of_dropoffs"), asc("DOLocationID"))
display(df_1a.limit(5))
// df_1a.limit(5).show()

// COMMAND ----------

// PART 1b: The top-5 most popular pickup locations - "PULocationID", sorted in descending order - if there is a tie, then one with lower "PULocationID" gets listed first 
// Output Schema: PULocationID int, number_of_pickups int


val df_1b = df_filter.select("PULocationID")
  .groupBy("PULocationID")
  .agg(count("PULocationID").alias("number_of_pickups"))
  .orderBy(desc("number_of_pickups"), asc("PULocationID"))

display(df_1b.limit(5))
// df_1b.limit(5).show()

// COMMAND ----------

// PART 2: List the top-3 locations with the maximum overall activity, i.e. sum of all pickups and all dropoffs at that LocationID. In case of a tie, the lower LocationID gets listed first.
// Output Schema: LocationID int, number_activities int

val df_joined = df_1a.join(df_1b, df_1a("DOLocationID") === df_1b("PULocationID"))
  .groupBy("DOLocationID")
  .agg((sum("number_of_pickups") + sum("number_of_dropoffs")).alias("number_activities"))

// df_joined.show()
val df_top = df_joined.orderBy(desc("number_activities"))
  .select(col("DOLocationID").alias("LocationID"), col("number_activities"))

// df_top.show()
display(df_top.limit(3))

// COMMAND ----------

// PART 3: List all the boroughs in the order of having the highest to lowest number of activities (i.e. sum of all pickups and all dropoffs at that LocationID), along with the total number of activity counts for each borough in NYC during that entire period of time.
// Output Schema: Borough string, total_number_activities int


val df3_joined = df_zone.join(df_top, df_zone("LocationID") === df_top("LocationID"))
                        .select("Borough", "number_activities")
                        .groupBy("Borough")
                        .agg(sum("number_activities").alias("total_number_activities"))
                        .orderBy(desc("total_number_activities"))

// display(df3_joined)
df3_joined.show()

// COMMAND ----------

// PART 4: List the top 2 days of week with the largest number of (daily) average pickups, along with the values of average number of pickups on each of the two days. The day of week should be a string with its full name, for example, "Monday" - not a number 1 or "Mon" instead.
// Output Schema: day_of_week string, avg_count float

val df4_1 = df_filter.select(to_date(col("pickup_datetime")).alias("temp_date"), 
                                  col("PULocationID"))
                              .groupBy("temp_date")
                            .agg(count("PULocationID").alias("count_pickups"))

val df4_2 = df4_1.select(date_format(to_date(col("temp_date"), "yyyy-MM-dd"), "EEEE").alias("day_of_week"), 
                                  col("count_pickups"))
                  .groupBy("day_of_week")
                   .agg(avg("count_pickups").alias("avg_count"))
                   .orderBy(desc("avg_count"))

df4_2.limit(2).show()

// COMMAND ----------

// PART 5: For each particular hour of a day (0 to 23, 0 being midnight) - in their order from 0 to 23, find the zone in Brooklyn borough with the LARGEST number of pickups. 
// Output Schema: hour_of_day int, zone string, max_count int

val window_spec_5 = Window.partitionBy("hour_of_day").orderBy(desc("count_pickups"))

val df5_joined = df_zone.join(df_filter, df_zone("LocationID") === df_filter("PULocationID"))
                        .filter(col("Borough") === "Brooklyn")
                        .select(col("zone"), hour(col("pickup_datetime")).alias("hour_of_day"))

val df5_max = df5_joined.groupBy("zone", "hour_of_day")
                        .agg(count("hour_of_day").as("count_pickups"))
                        .withColumn("max_count", max("count_pickups").over(window_spec_5))

val df5_result = df5_max.filter(col("count_pickups") === col("max_count"))
                      .orderBy("hour_of_day")
                      .select("hour_of_day", "zone", "max_count")


display(df5_result)


// COMMAND ----------

// PART 6 - Find which 3 different days of the January, in Manhattan, saw the largest percentage increment in pickups compared to previous day, in the order from largest increment % to smallest increment %. 
// Print the day of month along with the percent CHANGE (can be negative), rounded to 2 decimal places, in number of pickups compared to previous day.
// Output Schema: day int, percent_change float

val window_spec_6 = Window.orderBy(asc("day"))

val df6_joined = df_zone.join(df_filter, df_zone("LocationID") === df_filter("PULocationID"))
                        .filter(col("Borough") === "Manhattan")
                        .select((date_format(to_date(col("pickup_datetime")), "d").alias("day")).cast("int"))

val df6_int_result = df6_joined.groupBy("day")
                        .agg(count("day").as("count_pickups"))
                        .orderBy(asc("day"))
                        .withColumn("previous_value", lag(col("count_pickups"), 1).over(window_spec_6))
                        .filter(col("previous_value").isNotNull)
                        .withColumn("percent_change", round((col("count_pickups") - col("previous_value")) / col("previous_value"), 2))

val df6_result = df6_int_result.select("day", "percent_change")
                              .orderBy(desc("percent_change"))


display(df6_result.limit(3))


// COMMAND ----------


